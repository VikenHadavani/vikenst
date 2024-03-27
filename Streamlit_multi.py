import streamlit as st
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import string

# Load the dataset
@st.cache
def load_data():
    return pd.read_csv("WELFAKE_Dataset.csv", encoding='ISO-8859-1')

# Text preprocessing function
def transform_text(text):
    ps = PorterStemmer()
    text = nltk.word_tokenize(text)
    text = [ps.stem(word) for word in text if word.isalnum() and word not in stopwords.words('english') and word not in string.punctuation]
    return " ".join(text)

# Preprocess the data
def preprocess_data(data):
    # Fill missing values with empty strings
    data['title'] = data['title'].fillna('')
    data['text'] = data['text'].fillna('')
    
    # Convert to lowercase
    data['title'] = data['title'].str.lower()
    data['text'] = data['text'].str.lower()
    
    # Combine 'title' and 'text' columns
    data['transformed_text'] = data['title'] + ' ' + data['text']
    
    # Apply text transformation
    data['transformed_text'] = data['transformed_text'].apply(transform_text)
    
    return data

# Train the model
def train_model(X_train, y_train):
    tfidf = TfidfVectorizer(max_features=3000)
    X_train_tfidf = tfidf.fit_transform(X_train)
    mnb = MultinomialNB()
    mnb.fit(X_train_tfidf, y_train)
    return tfidf, mnb

# Main function
def main():
    st.title("Fake News Detection")

    # Load data
    data = load_data()
    data = preprocess_data(data)

    # Split data
    X = data['transformed_text']
    y = data['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2)

    # Train model
    tfidf, model = train_model(X_train, y_train)

    # User input
    input_text = st.text_input("Enter news text:")
    if st.button("Classify"):
        input_transformed = transform_text(input_text)
        input_tfidf = tfidf.transform([input_transformed])
        prediction = model.predict(input_tfidf)
        if prediction == 1:
            st.write("Predicted Label: Not Fake News")
        else:
            st.write("Predicted Label: Fake News")

    # Evaluation
    st.subheader("Model Evaluation")
    y_pred = model.predict(tfidf.transform(X_test))
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, fscore, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    confusion_mat = confusion_matrix(y_test, y_pred)
    st.write(f"Accuracy: {accuracy}")
    st.write(f"Precision: {precision}")
    st.write(f"Recall: {recall}")
    st.write(f"F1-score: {fscore}")
    st.write("Confusion Matrix:")
    st.write(confusion_mat)

    # Visualizations
    st.subheader("Visualizations")
    plt.figure(figsize=(15, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(data[data['label'] == 0]['num_characters'])
    sns.histplot(data[data['label'] == 1]['num_characters'], color='red')
    plt.title('Character Count Distribution')
    plt.legend(['Non-Fake News', 'Fake News'])

    plt.subplot(1, 2, 2)
    wc_true = WordCloud(width=600, height=600, min_font_size=10, background_color='white').generate(data[data['label'] == 1]['transformed_text'].str.cat(sep=" "))
    wc_false = WordCloud(width=600, height=600, min_font_size=10, background_color='white').generate(data[data['label'] == 0]['transformed_text'].str.cat(sep=" "))
    plt.imshow(wc_true)
    plt.title('Word Cloud - Fake News')
    plt.axis('off')

    plt.imshow(wc_false)
    plt.title('Word Cloud - Non-Fake News')
    plt.axis('off')

    st.pyplot()

if __name__ == "__main__":
    main()
