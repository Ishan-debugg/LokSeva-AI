import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

print("Loading dataset...")

df = pd.read_excel("../dataset/kdmc_data.xlsx")

df.rename(columns={
    "Complaint Description": "complaint",
    "Complaint Type": "category"
}, inplace=True)

df = df[['complaint', 'category']].dropna()

print(f"Dataset Loaded : {len(df)} complaints")

# Fast preprocessing
df["clean_text"] = (
    df["complaint"]
    .astype(str)
    .str.lower()
    .str.strip()
)

X = df["clean_text"]
y = df["category"]

print("Splitting dataset...")
# Remove nulls
df = df[['complaint', 'category']].dropna()

# Check all unique categories
print("\nCategory Counts:")
print(df["category"].value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Vectorizing...")

vectorizer = TfidfVectorizer(stop_words="english")

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("Training model...")

model = LogisticRegression(max_iter=500)

model.fit(X_train_vec, y_train)

print("Evaluating...")

y_pred = model.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted")
recall = recall_score(y_test, y_pred, average="weighted")
f1 = f1_score(y_test, y_pred, average="weighted")

print("\n========== MODEL PERFORMANCE ==========")

print(f"Accuracy : {accuracy*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
print(f"Recall   : {recall*100:.2f}%")
print(f"F1 Score : {f1*100:.2f}%")

print("\nClassification Report\n")

print(classification_report(y_test, y_pred))

print("\nConfusion Matrix\n")

print(confusion_matrix(y_test, y_pred))

print("\nTraining final model on full dataset...")

X_full = vectorizer.fit_transform(X)

model.fit(X_full, y)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\n✅ Model saved successfully!")