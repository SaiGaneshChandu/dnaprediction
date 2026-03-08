import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# load dataset
data = pd.read_csv("dataset/jaya_balanced_dataset.csv")

# correct columns
X = data['sequence']
y = data['class']

# convert DNA text → numeric features
vectorizer = CountVectorizer(analyzer='char', ngram_range=(4,4))
X_vec = vectorizer.fit_transform(X)

# split data
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

# train model
model = MultinomialNB()
model.fit(X_train, y_train)

# accuracy
accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

# save model
pickle.dump(model, open("models/dna_nb_model.pkl", "wb"))
pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

print("ML model saved ✅")
