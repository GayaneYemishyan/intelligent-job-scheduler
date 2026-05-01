# Intelligent Job Scheduler — Local Setup

## Directory Structure

```
intelligent-job-scheduler/
├── models/
│   ├── job_scheduler_model.pkl   ← download from HuggingFace
│   └── label_encoder.pkl         ← download from HuggingFace
├── app.py
├── index.html
└── requirements.txt
```

## 1 · Download Model Assets

From [https://huggingface.co/gayaneyemishyan/job-scheduler/tree/main](https://huggingface.co/gayaneyemishyan/job-scheduler/tree/main)
download both `.pkl` files and place them inside the `models/` folder.

```bash
mkdir -p models
# manually download or use huggingface_hub:
pip install huggingface_hub
python - <<'EOF'
from huggingface_hub import hf_hub_download
hf_hub_download("gayaneyemishyan/job-scheduler", "job_scheduler_model.pkl", local_dir="models")
hf_hub_download("gayaneyemishyan/job-scheduler", "label_encoder.pkl",       local_dir="models")
EOF
```

## 2 · Install Python Dependencies

```bash
pip install flask flask-cors scikit-learn numpy
```

## 3 · Run the Backend

```bash
python app.py
# → Running on http://0.0.0.0:5000
```

## 4 · Open the Frontend

Open `index.html` directly in your browser — no build step needed.
The frontend calls `http://localhost:5000/predict` via the Fetch API.

## API Reference

### `POST /predict`

**Body (JSON):**
```json
{
  "CPU_Usage_%": 72.5,
  "Memory_Usage_%": 55.0,
  "Network_Traffic_MBPS": 120,
  "Priority": "High"
}
```

**Response:**
```json
{
  "status": "Ready",
  "confidence": 91.4,
  "input": { ... }
}
```

**Priority values:** `Low` · `Medium` · `High` · `Urgent`

### `GET /health`
Returns model load status.

## Notes

- `flask-cors` is required so the HTML file (served from `file://`) can reach the Flask API.
- If confidence returns `null`, the model does not support `predict_proba` — this is normal for some serialised pipelines.
