"""Model loading and prediction helpers for MaizeSecure."""

import os
import tempfile
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

MODEL_PATH = Path("fall_armyworm_production_version_3/best.pt")
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/maizesecure_ultralytics")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/maizesecure_matplotlib")

CLASS_TO_SEVERITY = {
    "healthy": "Healthy",
    "early_to_moderate": "Early to Moderate",
    "severe": "Severe",
}
SEVERITY_COLORS = {
    "Healthy": "#38a357",
    "Early to Moderate": "#d6a900",
    "Severe": "#d63c3c",
}
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
IMAGE_SIZE = 640


@st.cache_resource(show_spinner=False)
def load_model():
    from ultralytics import YOLO

    return YOLO(str(MODEL_PATH))


def _blank_scores() -> dict[str, float]:
    return {"Healthy": 0.0, "Early to Moderate": 0.0, "Severe": 0.0}


def _error_result(message: str) -> dict:
    return {
        "severity": None,
        "confidence": 0,
        "scores": _blank_scores(),
        "source": "error",
        "error": message,
    }


def _run_inference(image: Image.Image):
    model = load_model()
    results = model.predict(
        image,
        conf=CONFIDENCE_THRESHOLD,
        iou=IOU_THRESHOLD,
        imgsz=IMAGE_SIZE,
        device="cpu",
        verbose=False,
    )
    return results[0]


def _extract_detections(result) -> list[dict]:
    detections = []
    if result.boxes is None:
        return detections

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = result.names[class_id]
        severity = CLASS_TO_SEVERITY.get(class_name)
        if severity is None:
            continue
        detections.append(
            {
                "class_id": class_id,
                "class_name": class_name,
                "severity": severity,
                "confidence": round(float(box.conf[0]) * 100, 1),
                "box": [round(float(value), 1) for value in box.xyxy[0].tolist()],
            }
        )
    return detections


def _annotate_image(image: Image.Image, detections: list[dict]) -> bytes:
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()

    for detection in detections:
        x1, y1, x2, y2 = [int(value) for value in detection["box"]]
        severity = detection["severity"]
        color = SEVERITY_COLORS[severity]
        label = f"{severity} {detection['confidence']:.0f}%"
        text_box = draw.textbbox((x1, y1), label, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        label_top = max(0, y1 - text_height - 8)

        draw.rectangle((x1, y1, x2, y2), outline=color, width=4)
        draw.rectangle(
            (x1, label_top, x1 + text_width + 8, label_top + text_height + 8),
            fill=color,
        )
        draw.text((x1 + 4, label_top + 4), label, fill="#ffffff", font=font)

    output = BytesIO()
    annotated.save(output, format="JPEG", quality=92)
    return output.getvalue()


def _image_prediction(image: Image.Image) -> dict:
    result = _run_inference(image)
    detections = _extract_detections(result)
    scores = _blank_scores()

    for detection in detections:
        severity = detection["severity"]
        scores[severity] = max(scores[severity], detection["confidence"])

    if not detections:
        return {
            "severity": None,
            "confidence": 0,
            "scores": scores,
            "source": "no_detection",
            "note": "No disease-stage detection found.",
            "detections": [],
            "class_counts": {},
        }

    severity = max(scores, key=scores.get)
    return {
        "severity": severity,
        "confidence": int(round(scores[severity])),
        "scores": scores,
        "source": "model",
        "detections": detections,
        "class_counts": dict(Counter(item["severity"] for item in detections)),
        "annotated_image": _annotate_image(image, detections),
    }


def predict_leaf_image(uploaded_file) -> dict:
    """Run YOLO inference for one image and return UI-compatible results."""
    if uploaded_file is None:
        return _error_result("No image was provided.")
    if not MODEL_PATH.exists():
        return _error_result(f"Model file not found: {MODEL_PATH}")

    try:
        image = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
        return _image_prediction(image)
    except Exception as exc:
        return _error_result(str(exc))


def predict_video(video_file, sample_count: int = 8) -> tuple[dict, bytes | None]:
    """Sample a video, aggregate frame-level detections, and return a representative frame."""
    if video_file is None:
        return _error_result("No video was provided."), None
    if not MODEL_PATH.exists():
        return _error_result(f"Model file not found: {MODEL_PATH}"), None

    try:
        import cv2
    except ImportError:
        return _error_result("Video support requires opencv-python-headless."), None

    suffix = Path(getattr(video_file, "name", "upload.mp4")).suffix or ".mp4"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
            temp_video.write(video_file.getvalue())
            temp_path = Path(temp_video.name)

        capture = cv2.VideoCapture(str(temp_path))
        if not capture.isOpened():
            return _error_result("Could not read the uploaded video."), None

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total_frames <= 0:
            capture.release()
            return _error_result("The uploaded video contains no readable frames."), None

        frames_to_sample = min(max(1, sample_count), total_frames)
        if frames_to_sample == 1:
            frame_indices = [0]
        else:
            frame_indices = [
                round(index * (total_frames - 1) / (frames_to_sample - 1))
                for index in range(frames_to_sample)
            ]

        counts: Counter[str] = Counter()
        confidences: dict[str, list[float]] = defaultdict(list)
        all_detections = []
        best_frame = None
        best_annotated = None
        best_confidence = -1.0
        processed = 0

        for frame_index in frame_indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame_bgr = capture.read()
            if not ok:
                continue

            processed += 1
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            result = _run_inference(image)
            detections = _extract_detections(result)

            for detection in detections:
                severity = detection["severity"]
                counts[severity] += 1
                confidences[severity].append(detection["confidence"])
                all_detections.append({**detection, "frame": frame_index})

            frame_best = max(
                (detection["confidence"] for detection in detections),
                default=0.0,
            )
            if best_frame is None or frame_best > best_confidence:
                best_frame = image
                best_annotated = _annotate_image(image, detections)
                best_confidence = frame_best

        capture.release()

        if processed == 0:
            return _error_result("Could not extract readable frames from the video."), None
        if not counts:
            return {
                "severity": None,
                "confidence": 0,
                "scores": _blank_scores(),
                "source": "no_detection",
                "note": "No disease-stage detection found in sampled video frames.",
                "detections": [],
                "class_counts": {},
                "frames_processed": processed,
            }, _image_to_jpeg(best_frame)

        severity = max(
            counts,
            key=lambda label: (counts[label], max(confidences[label])),
        )
        confidence = round(sum(confidences[severity]) / len(confidences[severity]))
        scores = _blank_scores()
        for label, values in confidences.items():
            scores[label] = round(max(values), 1)

        representative_image = _image_to_jpeg(best_frame)
        return {
            "severity": severity,
            "confidence": int(confidence),
            "scores": scores,
            "source": "video_model",
            "detections": all_detections,
            "class_counts": dict(counts),
            "frames_processed": processed,
            "annotated_image": best_annotated,
            "note": "Video result is based on sampled frame-level detections.",
        }, representative_image
    except Exception as exc:
        return _error_result(str(exc)), None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _image_to_jpeg(image: Image.Image | None) -> bytes | None:
    if image is None:
        return None
    output = BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=92)
    return output.getvalue()
