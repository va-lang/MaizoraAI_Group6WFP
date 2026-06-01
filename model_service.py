"""Model loading and prediction helpers for MaizoraAI."""

import os
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

MODEL_PATH = Path("maize_model_production_results/best.pt")
os.environ.setdefault("YOLO_CONFIG_DIR", "/private/tmp/maizora_ultralytics")
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/maizora_matplotlib")
CLASS_TO_SEVERITY = {
    "healthy": "Healthy",
    "early stage": "Early",
    "late stage": "Severe",
}
CONFIDENCE_THRESHOLD = 0.25


@st.cache_resource(show_spinner=False)
def load_model():
    from ultralytics import YOLO

    return YOLO(str(MODEL_PATH))


def _blank_scores() -> dict[str, float]:
    return {"Healthy": 0.0, "Early": 0.0, "Severe": 0.0}


def predict_leaf_image(uploaded_file) -> dict:
    """Run YOLO inference and return the same result shape used by the UI."""
    if uploaded_file is None:
        return {
            "severity": None,
            "confidence": 0,
            "scores": _blank_scores(),
            "source": "error",
            "error": "No image was provided.",
        }

    if not MODEL_PATH.exists():
        return {
            "severity": None,
            "confidence": 0,
            "scores": _blank_scores(),
            "source": "error",
            "error": f"Model file not found: {MODEL_PATH}",
        }

    try:
        image = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
        model = load_model()
        results = model.predict(image, conf=CONFIDENCE_THRESHOLD, imgsz=640, verbose=False)
        detections = results[0]
        scores = _blank_scores()

        for box in detections.boxes:
            class_id = int(box.cls[0])
            class_name = detections.names[class_id]
            severity = CLASS_TO_SEVERITY.get(class_name)
            if severity is None:
                continue
            confidence = round(float(box.conf[0]) * 100, 1)
            scores[severity] = max(scores[severity], confidence)

        if max(scores.values()) == 0:
            return {
                "severity": None,
                "confidence": 0,
                "scores": scores,
                "source": "no_detection",
                "note": "No disease-stage detection found.",
            }

        severity = max(scores, key=scores.get)
        return {
            "severity": severity,
            "confidence": int(round(scores[severity])),
            "scores": scores,
            "source": "model",
        }
    except Exception as exc:
        return {
            "severity": None,
            "confidence": 0,
            "scores": _blank_scores(),
            "source": "error",
            "error": str(exc),
        }
