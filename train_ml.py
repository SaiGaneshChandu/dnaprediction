import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib, os

# load dataset
data = pd.read_csv(
    r"C:\Users\dell\Desktop\SaiGanesh\Main Project\app7\dataset\jaya_balanced_dataset.csv"
)

print("Dataset Loaded:", data.shape)

# ===== convert DNA to k-mer tokens =====
def kmer_tokenizer(seq, k=10):
    return [seq[i:i+k] for i in range(len(seq)-k+1)]

# vectorize sequences (counts work better for NB)
vectorizer = CountVectorizer(
    analyzer=kmer_tokenizer,
    lowercase=False
)

X = vectorizer.fit_transform(data['sequence'])

# encode labels
le = LabelEncoder()
y = le.fit_transform(data['class'])

# stratified split keeps class balance
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Multinomial NB with tuned smoothing
model = MultinomialNB(alpha=0.01)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

# save
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/ml_model.pkl")
joblib.dump(le, "models/label_encoder.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("Training Complete")
