import pickle
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Model loading ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "job_scheduler_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoder.pkl")

PRIORITY_MAP = {"Low": 0, "Medium": 1, "High": 2, "Urgent": 3}

def load_artifacts():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
    return model, label_encoder

try:
    model, label_encoder = load_artifacts()
    print("[OK] Model and label encoder loaded successfully.")
except FileNotFoundError as e:
    model, label_encoder = None, None
    print(f"[WARN] Could not load model artifacts: {e}")


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "encoder_loaded": label_encoder is not None
    })


@app.route("/predict", methods=["POST"])
def predict():
    if model is None or label_encoder is None:
        return jsonify({"error": "Model artifacts not loaded. Check server logs."}), 503

    data = request.get_json(force=True)

    # ── Validate inputs ────────────────────────────────────────────────────────
    required = ["CPU_Usage_%", "Memory_Usage_%", "Network_Traffic_MBPS", "Priority"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    priority_raw = data["Priority"]
    if priority_raw not in PRIORITY_MAP:
        return jsonify({"error": f"Priority must be one of {list(PRIORITY_MAP.keys())}"}), 400

    # ── Build feature vector ───────────────────────────────────────────────────
    priority_encoded = PRIORITY_MAP[priority_raw]
    features = np.array([[
        float(data["CPU_Usage_%"]),
        float(data["Memory_Usage_%"]),
        float(data["Network_Traffic_MBPS"]),
        priority_encoded
    ]])

    # ── Inference ─────────────────────────────────────────────────────────────
    prediction_encoded = model.predict(features)[0]
    prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

    # Probability scores (if the model supports it)
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        confidence = round(float(np.max(proba)) * 100, 2)

    return jsonify({
        "status": prediction_label,
        "confidence": confidence,
        "input": {
            "CPU_Usage_%": data["CPU_Usage_%"],
            "Memory_Usage_%": data["Memory_Usage_%"],
            "Network_Traffic_MBPS": data["Network_Traffic_MBPS"],
            "Priority": priority_raw,
            "Priority_encoded": priority_encoded
        }
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
