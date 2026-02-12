import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Simple training data (prototype)
texts = [
    "Breaking news: government announces new policy",
    "You won 1 crore lottery click here now",
    "Official press release from finance ministry",
    "Shocking secret investment scheme double money fast",
]

labels = [0, 1, 0, 1]  # 0 = Real, 1 = Fake

# Vectorize text
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Train model
model = LogisticRegression()
model.fit(X, labels)

# Save model and vectorizer
joblib.dump(model, "models/text_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("Text model saved successfully.")
