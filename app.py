import os

# TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from collections import Counter
import warnings
import logging
from sklearn.exceptions import InconsistentVersionWarning



# Suppress sklearn version warning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# ----------------
# Load Model, Tokenizer, and Label Encoder
# ----------------
# model = load_model("lstm_model.keras")

model = None

def get_model():
    global model
    if model is None:
        model = load_model("lstm_model.keras")
    return model

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Make sure this matches training time
MAXLEN = 100  

# ----------------
# Flask setup
# ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Flask/YT_sentiment_analysis"

@app.route("/healthz")
def health():
    return "OK", 200

# Mapping for readability
class_map = {
    -1: "Negative",
     0: "Neutral",
     1: "Positive"
}

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    comments = data.get("comments", [])

    if not comments:
        return jsonify({"error": "No comments provided"}), 400

    # Convert text → sequences
    model = get_model()

    sequences = tokenizer.texts_to_sequences(comments)
    padded = pad_sequences(sequences, maxlen=MAXLEN)

    # Predict probabilities
    preds = model.predict(padded)

    # Instead of argmax, use label_encoder to map directly
    pred_classes = label_encoder.inverse_transform(np.argmax(preds, axis=1))

    # Decode numeric → sentiment
    decoded = [class_map[int(p)] for p in pred_classes]

    # Count sentiments
    counts = Counter(decoded)
    overall_sentiment = max(counts, key=counts.get) if counts else "Unknown"

    # Get top 10 positive comments
    positive_comments = [
        comment for comment, sentiment in zip(comments, decoded) if sentiment == "Positive"
    ][:10]

    return jsonify({
        "overall_sentiment": overall_sentiment,
        "total_positive": counts.get("Positive", 0),
        "total_negative": counts.get("Negative", 0),
        "total_neutral": counts.get("Neutral", 0),
        "top_10_positive_comments": positive_comments
    })

if __name__ == "__main__":
    app.run(debug=False)
