"""
predict.py
─────────────────────────────────────────────────────────────────────────────
Two-layer classification pipeline:

  Layer 1 — Keyword Rule Engine (fast, deterministic)
    Checks the raw complaint text against high-confidence keyword rules.
    If a match is found the department is returned immediately — no ML needed.
    This catches "power cut", "no electricity", "paani nahi", etc. perfectly
    regardless of how the ML model was trained.

  Layer 2 — TF-IDF + Logistic Regression (ML fallback)
    For ambiguous complaints that don't match any keyword rule, the text is
    preprocessed (Devanagari + transliteration expansion) and passed through
    the trained ML model.
─────────────────────────────────────────────────────────────────────────────
"""

import pickle
from preprocess import preprocess_text, keyword_department_override

# Load trained model and vectorizer once at startup
model      = pickle.load(open("model.pkl",      "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))


def predict_category(text: str) -> str:
    """
    Returns the predicted department category string.
    Uses keyword rules first, falls back to ML model.
    """
    if not text or not isinstance(text, str):
        return "General"

    # ── Layer 1: Keyword Rule Engine ──────────────────────────────────────
    # Check both the raw text and the lowercased version.
    # This catches English keywords without any preprocessing.
    keyword_hit = keyword_department_override(text)
    if keyword_hit:
        return keyword_hit

    # ── Layer 2: ML Model Fallback ────────────────────────────────────────
    # Preprocess expands Hindi/Marathi keywords into English so TF-IDF
    # can match the vocabulary it was trained on.
    processed = preprocess_text(text)

    # After preprocessing, run the keyword check again — the expansion
    # may have introduced recognisable English terms (e.g. "बिजली" →
    # "electricity electric power") that match rules now.
    keyword_hit_post = keyword_department_override(processed)
    if keyword_hit_post:
        return keyword_hit_post

    # Final fallback: TF-IDF vectorization + Logistic Regression
    vec = vectorizer.transform([processed])
    return model.predict(vec)[0]
