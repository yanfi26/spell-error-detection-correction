import string
import streamlit as st

from utils.correction.main_correction import generate_corrected_sentence
from utils.text_preprocessing import text_preprocessing
from utils.load_model import load_model

# From detection folder
from utils.detection.tokenizer import tokenization
from utils.detection.get_word_index import get_word_index
from utils.detection.padding_sequencing import padding_sequencing
from utils.detection.embedding import embedding
from utils.detection.show_text_prediction import show_text_prediction

# From correction folder
from utils.correction.load_dictionary import load_dictionary
from utils.correction.conditional_clean_sentence import conditional_clean_sentence

# Variables
model_corr_fn = './models/model_bilstm-mh_attm_epoch-100_batch-64_BI.h5'

model_det_fn = './models/word_error_detection_all_subjects.h5'

# Header
header_left, header_right = st.columns([1,5], vertical_alignment="center")

with header_left:
    st.image("assets/peka.png", width=120)

with header_right:
    st.subheader('Pendeteksi dan Koreksi Ejaan')

# Input
input_text = st.text_area('Masukkan kalimat')

# Create a placeholder for the button
submit = st.button('Koreksi', key='tombol_koreksi')

# Text preprocessing
text = text_preprocessing(input_text)

# Create encode and decode dictionary
char_set = list(" abcdefghijklmnopqrstuvwxyz0123456789") + [x for x in string.punctuation]
char2int = { char_set[x]:x for x in range(len(char_set)) }
int2char = { char2int[x]:x for x in char_set }

# Add escape character to encode and decode characters
count = len(char_set)
codes = ["\t","\n"]
for i in range(len(codes)):
    code = codes[i]
    char2int[code] = count
    int2char[count] = code
    count+=1

# Load correction model   
model_corr = load_model(model_corr_fn)

# Load detection models
model_det = load_model(model_det_fn)

# Load dictionary
my_dictionary = load_dictionary("./my_dictionary.txt")
sastrawi_dictionary = load_dictionary("./sastrawi_dictionary.txt")

# Detection sentence
if submit:
    detection_result = 0
    # Tokenization
    input_seq = tokenization(text)

    # Padding Sequencing
    input_seq_pad = padding_sequencing(input_seq)

    # Split words
    def split_word(sentence: str): return sentence.split(' ')

    words = split_word(text)

    # Get word index
    word_index = get_word_index(text)

    # Embedding
    embedding_matrix = embedding(words, word_index)

    # Detection
    y_pred = model_det.predict(embedding_matrix, verbose=0).argmax(axis=-1)

    # Detect the wrong word
    for word_idx, word in enumerate(text.split()):
      if word not in my_dictionary:
        show_text_prediction(1)
        detection_result = 1
        break

    # Correction sentence
    if detection_result == 1:

        sentence = generate_corrected_sentence(sastrawi_dictionary, my_dictionary, char_set, char2int, int2char, model_corr, text)
        transformed_sentence = conditional_clean_sentence(sentence, input_text)

        with st.spinner('Sedang mengkoreksi...'):
            st.subheader("Hasil koreksi:")
            st.info(transformed_sentence)

            with st.popover("Koreksi kalimat, jika kalimat salah", use_container_width=True):
                correct_sentence = st.text_area("Kalimat yang benar menurut anda adalah:")
    else:
        show_text_prediction(0)