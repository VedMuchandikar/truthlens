from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import re
from typing import Optional
import os

app = FastAPI(
    title="TruthLens ML Service",
    description="Text classification API — Phase 1 baseline",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model at startup ──────────────────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "model/classifier.pkl")

@app.on_event("startup")
def load_model():
    global pipeline
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run train.py first.")
    pipeline = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")

# ── Schemas ────────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    input_type: Optional[str] = Field(default="TEXT", description="TEXT | URL | EMAIL | WHATSAPP")

class TokenWeight(BaseModel):
    word: str
    weight: float

class PredictResponse(BaseModel):
    verdict: str                    # GENUINE | SCAM | SUSPICIOUS
    confidence: float               # 0.0 – 1.0
    probabilities: dict[str, float]
    top_features: list[TokenWeight] # words that drove the decision
    input_type: str

# ── Helpers ────────────────────────────────────────────────────────────────────
SUSPICIOUS_PATTERNS = [
    r"\b(free|win|won|prize|claim|urgent|click|verify|suspend)\b",
    r"http[s]?://bit\.ly|tinyurl|goo\.gl",
    r"₹\s*\d+|\$\s*\d+",
    r"\b(guaranteed|limited|offer|congratulations)\b",
]

def get_top_features(text: str, n: int = 10) -> list[dict]:
    """
    Extract which words pushed the prediction toward SCAM.
    Uses the TF-IDF weights × logistic regression coefficients.
    """
    vectorizer = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    # Get TF-IDF feature names and the transformed vector for this text
    feature_names = vectorizer.get_feature_names_out()
    tfidf_matrix = vectorizer.transform([text])

    # SCAM class index
    classes = list(clf.classes_)
    scam_idx = classes.index("SCAM") if "SCAM" in classes else 0

    # Multiply TF-IDF weights by logistic regression coefficients
    if clf.coef_.shape[0] == 1:
        coef = clf.coef_[0]
    else:
        coef = clf.coef_[scam_idx]  # shape: (n_features,)
    tfidf_weights = tfidf_matrix.toarray()[0]  # shape: (n_features,)
    contribution = tfidf_weights * coef

    # Get top N features by absolute contribution
    top_indices = np.argsort(np.abs(contribution))[::-1][:n]
    results = []
    for idx in top_indices:
        if tfidf_weights[idx] > 0:  # only words actually in the input
            results.append({
                "word": feature_names[idx],
                "weight": round(float(contribution[idx]), 4),
            })

    return results[:n]

def classify_confidence(verdict: str, confidence: float) -> str:
    """Downgrade to SUSPICIOUS if model is uncertain."""
    if verdict == "SCAM" and confidence < 0.65:
        return "SUSPICIOUS"
    return verdict

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "TF-IDF + LogisticRegression v1"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # Predict
    proba = pipeline.predict_proba([text])[0]
    classes = list(pipeline.classes_)
    prob_map = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}

    scam_prob = prob_map.get("SCAM", 0)

    if scam_prob >= 0.35:
        raw_verdict = "SCAM"
    else:
        raw_verdict = "GENUINE"

    confidence = round(float(max(proba)), 4)
    verdict = classify_confidence(raw_verdict, confidence)

    top_features = get_top_features(text)

    return PredictResponse(
        verdict=verdict,
        confidence=confidence,
        probabilities=prob_map,
        top_features=[TokenWeight(**f) for f in top_features],
        input_type=req.input_type or "TEXT",
    )

@app.get("/")
def root():
    return {"message": "TruthLens ML Service — Phase 1"}