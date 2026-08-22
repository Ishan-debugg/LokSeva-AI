"""
app.py — LokSevaAI ML Service
─────────────────────────────────────────────────────────────────────────────
Endpoints:
  POST /predict       — Main classification endpoint
  POST /detect_lang   — Utility: detect language of input text
  GET  /health        — Health check
─────────────────────────────────────────────────────────────────────────────
"""

from flask import Flask, request, jsonify
from predict import predict_category
from preprocess import keyword_department_override, preprocess_text

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Classify a complaint into a department.

    Request body:
        { "complaint": "<raw text in any language>" }

    Response:
        {
            "category":   "<department_key>",
            "method":     "keyword_rule" | "ml_model",
            "processed":  "<preprocessed text sent to ML>"
        }
    """
    data      = request.json or {}
    complaint = data.get("complaint", "").strip()

    if not complaint:
        return jsonify({"error": "complaint field is required"}), 400

    # Check keyword layer first (fast path)
    kw_hit = keyword_department_override(complaint)
    if kw_hit:
        return jsonify({
            "category": kw_hit,
            "method":   "keyword_rule",
            "processed": complaint.lower()
        })

    # ML fallback path
    processed = preprocess_text(complaint)

    # Post-preprocessing keyword check
    kw_hit_post = keyword_department_override(processed)
    if kw_hit_post:
        return jsonify({
            "category": kw_hit_post,
            "method":   "keyword_rule_post_preprocess",
            "processed": processed
        })

    # Full ML prediction
    category = predict_category(complaint)
    return jsonify({
        "category": category,
        "method":   "ml_model",
        "processed": processed
    })


@app.route("/detect_lang", methods=["POST"])
def detect_lang():
    """
    Detect the language of the input text.
    Returns: { "language": "en" | "hi" | "mr" | "unknown" }
    """
    data = request.json or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"language": "unknown"})

    # Simple heuristic: check for Devanagari Unicode range (0900–097F)
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total_chars = len([c for c in text if c.strip()])

    if total_chars == 0:
        return jsonify({"language": "unknown"})

    devanagari_ratio = devanagari_chars / total_chars

    if devanagari_ratio > 0.3:
        # Could be Hindi or Marathi — both use Devanagari
        # Marathi-specific words
        marathi_words = ["आहे", "नाही", "आमच्या", "भागात", "आहेत",
                         "येत", "काढा", "तुंबले"]
        hindi_words   = ["है", "नहीं", "हमारे", "हो", "रहा",
                         "गया", "हटाओ", "आ"]
        mr_score = sum(1 for w in marathi_words if w in text)
        hi_score = sum(1 for w in hindi_words   if w in text)
        lang = "mr" if mr_score >= hi_score else "hi"
    else:
        lang = "en"

    return jsonify({"language": lang})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "LokSevaAI ML Service"})


if __name__ == "__main__":
    print("🚀 LokSevaAI ML Service starting on port 5000...")
    print("   Languages supported: English, Hindi, Marathi")
    print("   Classification layers: Keyword Rules + TF-IDF Logistic Regression")
    app.run(port=5000, debug=False)
    