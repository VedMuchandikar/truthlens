import pandas as pd
import numpy as np
import joblib
import os
import requests
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# ── 1. Download dataset ────────────────────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
DATA_PATH = "model/sms_spam.tsv"

os.makedirs("model", exist_ok=True)

if not os.path.exists(DATA_PATH):
    print("Downloading SMS Spam Collection dataset...")
    r = requests.get(DATA_URL, timeout=30)
    with open(DATA_PATH, "wb") as f:
        f.write(r.content)
    print("Downloaded.")
else:
    print("Dataset already exists, skipping download.")

# ── 2. Load & inspect ──────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, sep="\t", header=None, names=["label", "text"])
print(f"\nDataset shape: {df.shape}")
print(df["label"].value_counts())

# Map to our verdict system
label_map = {"ham": "GENUINE", "spam": "SCAM"}
df["verdict"] = df["label"].map(label_map)

# ── 3. Train/val split ─────────────────────────────────────────────────────────
X = df["text"]
y = df["verdict"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

# ── 4. Build pipeline ──────────────────────────────────────────────────────────
# TfidfVectorizer converts text → sparse feature matrix
# LogisticRegression classifies with calibrated probabilities
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),   # unigrams + bigrams
        stop_words="english",
        sublinear_tf=True,    # apply log(1+tf) to dampen high freq terms
    )),
    ("clf", LogisticRegression(
        max_iter=2000,
        C=5.0,                # regularization — tune if needed
        class_weight="balanced",  # handles class imbalance automatically
        solver="lbfgs",
    )),
])

# ── 5. Train ───────────────────────────────────────────────────────────────────
print("\nTraining model...")
pipeline.fit(X_train, y_train)

# ── 6. Evaluate ───────────────────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
print("\n── Evaluation Report ──")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ── 7. Save model ─────────────────────────────────────────────────────────────
MODEL_PATH = "model/classifier.pkl"
joblib.dump(pipeline, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")

# ── 8. Quick sanity check ─────────────────────────────────────────────────────
test_cases = [
    "Congratulations! You've won a FREE iPhone. Click now to claim.",
    "Hey, are we still meeting at 6pm today?",
    "URGENT: Your account is suspended. Verify immediately at bit.ly/xxx",
    "Can you send me the notes from yesterday's lecture?",
]

loaded = joblib.load(MODEL_PATH)
print("\n── Sanity Checks ──")
for text in test_cases:
    pred = loaded.predict([text])[0]
    prob = loaded.predict_proba([text])[0]
    classes = loaded.classes_
    confidence = max(prob)
    print(f"[{pred} | {confidence:.0%}] {text[:60]}...")