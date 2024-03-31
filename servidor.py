from flask import Flask, request, jsonify
from flask_cors import CORS 
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib
import logging
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Carregar os dados
df = pd.read_csv('dataset_noticias.csv')

# Remover as palavras de parada (stop words) em português
stop_words = stopwords.words('portuguese')

# Reduzir as palavras para sua forma canônica (lemmatization)
lemmatizer = WordNetLemmatizer()
df['news_no_stopwords'] = df['preprocessed_news'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

# Dividir os dados em conjunto de treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(df['news_no_stopwords'], df['label'], test_size=0.2, random_state=42)

# Pré-processamento de texto e vetorização
tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words)
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)

# Treinamento do modelo
clf = MultinomialNB()
clf.fit(X_train_tfidf, y_train)

# Salvar o modelo treinado
joblib.dump(clf, 'model.pkl')

# Função de pré-processamento do texto da notícia
def preprocess_text(news_text):
    return ' '.join([lemmatizer.lemmatize(word) for word in news_text.split() if word.lower() not in stop_words])

def predict_fake_news(news_text):
    preprocessed_news_text = preprocess_text(news_text)
    fake_probability = clf.predict_proba(tfidf_vectorizer.transform([preprocessed_news_text]))[0][1]  # Obtém a probabilidade da classe "falsa"
    return fake_probability

# Configurar o logger
logging.basicConfig(level=logging.INFO)  # Definir o nível de logging para INFO

@app.route('/detect-fake-news', methods=['POST'])
def detect_fake_news():
    if request.method == 'POST':
        try:
            data = request.get_json()

            if 'news_text' not in data:
                raise ValueError("O campo 'news_text' é obrigatório.")

            news_text = data['news_text']
            
            # Fazer a previsão usando o modelo
            fake_probability = predict_fake_news(news_text)

            # Adicionar informações ao log
            logging.info(f"Texto da notícia: {news_text}")
            logging.info(f"Probabilidade de ser fake news: {fake_probability}")

            return jsonify({'fake_probability': fake_probability})
        except ValueError as ve:
            logging.error("Erro ao detectar fake news:", ve)
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logging.error("Erro ao detectar fake news:", e)
            return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    app.run()
