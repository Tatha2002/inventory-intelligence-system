
import re
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize_text(text):
    cleaned_text = clean_text(text)
    return word_tokenize(cleaned_text)


def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word not in stop_words]


def preprocess_complaint(text):
    tokens = tokenize_text(text)
    filtered_tokens = remove_stopwords(tokens)
    processed_text = ' '.join(filtered_tokens)
    return processed_text


def get_pos_tags(text):
    processed_text = preprocess_complaint(text)
    tokens = word_tokenize(processed_text)
    return pos_tag(tokens)


def vectorize_complaints(complaint_texts):
    processed_texts = [preprocess_complaint(text) for text in complaint_texts]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    return vectorizer, tfidf_matrix
