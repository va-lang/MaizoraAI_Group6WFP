"""
FAW Detection Streamlit App
============================
Inputs  : Image | Video | Webcam/Camera
Model   : YOLOv8 (best.pt from training pipeline)
Classes : 0=healthy_maize | 1=early_stage | 2=late_stage
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import time
import collections
import os
from pathlib import Path
from PIL import Image
import io

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FAW Detection System",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;800&display=swap');

:root {
    --green:   #00c896;
    --amber:   #f5a623;
    --red:     #e84040;
    --bg:      #0d1117;
    --surface: #161b22;
    --border:  #30363d;
    --text:    #e6edf3;
    --muted:   #8b949e;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Main header */
.app-header {
    background: linear-gradient(135deg, #0d2b1f 0%, #0d1117 60%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,200,150,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.app-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 4px 0;
    background: linear-gradient(90deg, #00c896, #00e8b0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.app-header p {
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 300;
}

/* Metric cards */
.metric-row { display: flex; gap: 12px; margin: 16px 0; }
.metric-card {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-card .val {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-card .lbl {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.val-green { color: var(--green); }
.val-amber { color: var(--amber); }
.val-red   { color: var(--red); }
.val-blue  { color: #58a6ff; }

/* Recommendation card */
.reco-card {
    border-radius: 12px;
    padding: 22px 26px;
    margin-top: 20px;
    border-left: 5px solid;
}
.reco-healthy {
    background: rgba(0,200,150,0.08);
    border-color: var(--green);
}
.reco-early {
    background: rgba(245,166,35,0.08);
    border-color: var(--amber);
}
.reco-late {
    background: rgba(232,64,64,0.08);
    border-color: var(--red);
}
.reco-mixed {
    background: rgba(88,166,255,0.08);
    border-color: #58a6ff;
}
.reco-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.reco-body {
    font-size: 0.88rem;
    color: var(--muted);
    line-height: 1.7;
}

/* Progress bars */
.class-bar-wrap { margin: 8px 0; }
.class-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    margin-bottom: 4px;
}
.class-bar-track {
    height: 10px;
    background: var(--border);
    border-radius: 99px;
    overflow: hidden;
}
.class-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s ease;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 24px; }

/* Buttons */
.stButton > button {
    background: var(--green) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Sora', sans-serif !important;
    padding: 10px 24px !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #00e8b0 !important;
    transform: translateY(-1px);
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--muted);
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: var(--green) !important;
    color: #000 !important;
}

/* Slider */
.stSlider [data-testid="stSlider"] > div > div > div {
    background: var(--green) !important;
}

hr { border-color: var(--border); }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
CLASS_NAMES   = ['healthy_maize', 'early_stage', 'late_stage']
CLASS_COLORS_BGR = {
    0: (0, 200, 150),   # green  — healthy
    1: (35, 166, 245),  # amber  — early
    2: (64, 64, 232),   # red    — late
}
CLASS_COLORS_HEX = {0: '#00c896', 1: '#f5a623', 2: '#e84040'}
CLASS_ICONS      = {0: '🟢', 1: '🟡', 2: '🔴'}

RECOMMENDATIONS = {
    0: {
        "title": "✅ Healthy Crop — No Immediate Action Required",
        "body": (
            "Your maize crop appears healthy with no visible Fall Armyworm activity. "
            "Continue routine scouting every 3–5 days during the critical seedling to "
            "V6 growth stages. Maintain field hygiene by removing weeds that serve as "
            "alternate hosts. Consider preventative application of biological agents such "
            "as <em>Bacillus thuringiensis</em> (Bt) or <em>Metarhizium</em> if FAW pressure "
            "is reported in surrounding fields. Record scouting dates for traceability."
        ),
        "css_class": "reco-healthy",
    },
    1: {
        "title": "⚠️ Early Stage Detected — Intervene Promptly",
        "body": (
            "Egg masses or young larvae (instars 1–3) have been detected. This is the "
            "<strong>optimal intervention window</strong> — larvae are still small, surface-feeding, "
            "and highly susceptible. Recommended actions:<br>"
            "• Apply <em>Bacillus thuringiensis</em> (Bt) or spinosad-based biopesticides "
            "into the leaf whorl where larvae congregate.<br>"
            "• Chemical option: emamectin benzoate or chlorantraniliprole at label rate.<br>"
            "• Scout the entire field to estimate infestation density (threshold: >20% plants infested).<br>"
            "• Revisit in 5–7 days to confirm control efficacy.<br>"
            "Early intervention can prevent yield losses of up to 40%."
        ),
        "css_class": "reco-early",
    },
    2: {
        "title": "🚨 Late Stage Detected — Urgent Damage Control",
        "body": (
            "Frass deposits and/or significant larval feeding damage are present, "
            "indicating mature larvae (instars 4–6) or established infestations. At this "
            "stage, larvae are deeply embedded in the whorl and harder to reach. "
            "Recommended actions:<br>"
            "• Apply systemic or contact insecticides such as chlorpyrifos, lambda-cyhalothrin, "
            "or emamectin benzoate with a surfactant to improve penetration into the whorl.<br>"
            "• Focus spray into the leaf whorl — not on leaf surfaces.<br>"
            "• Assess crop damage level: if >50% of plants show severe damage at early "
            "growth stages, consider replanting or supplemental planting.<br>"
            "• Document damage for insurance or government support schemes.<br>"
            "• Implement pheromone traps to monitor adult moth populations post-intervention."
        ),
        "css_class": "reco-late",
    },
}

MIXED_RECO = {
    "title": "📊 Mixed Infestation — Tiered Response Strategy",
    "body": (
        "Multiple infestation stages were detected across this input. Apply a tiered "
        "response based on the dominant class percentage shown above. Prioritise treatment "
        "of late-stage damage zones first, then address early-stage areas to prevent "
        "progression. Use the class distribution breakdown to allocate field resources "
        "and treatment volumes proportionally. Re-scout within 5–7 days to track progression."
    ),
    "css_class": "reco-mixed",
}


# ──────────────────────────────────────────────────────────────────────────────
# MODEL LOADING
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model(model_path: str):
    try:
        from ultralytics import YOLO
        return YOLO(model_path), None
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────────────────────────────────────
# PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────
def preprocess_image(pil_img: Image.Image, target_size: int = 640) -> np.ndarray:
    """
    Resize with letterboxing to preserve aspect ratio, convert to RGB uint8.
    Returns the preprocessed PIL image (YOLO model handles final tensor conversion).
    """
    img = pil_img.convert("RGB")
    # Letterbox: pad to square without distorting
    w, h  = img.size
    scale = target_size / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized  = img.resize((new_w, new_h), Image.LANCZOS)
    canvas       = Image.new("RGB", (target_size, target_size), (114, 114, 114))
    canvas.paste(img_resized, ((target_size - new_w) // 2, (target_size - new_h) // 2))
    return canvas


def preprocess_frame(frame_bgr: np.ndarray) -> np.ndarray:
    """Preprocess a raw BGR video/webcam frame for YOLO inference."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    return frame_rgb


# ──────────────────────────────────────────────────────────────────────────────
# INFERENCE & DRAWING
# ──────────────────────────────────────────────────────────────────────────────
def run_inference(model, source, conf_thresh: float, iou_thresh: float):
    """Run YOLO inference. source can be PIL.Image or np.ndarray (RGB)."""
    results = model.predict(
        source=source,
        conf=conf_thresh,
        iou=iou_thresh,
        verbose=False,
        device="cpu",   # Streamlit Cloud uses CPU; change to 0 for local GPU
    )
    return results[0]


def draw_boxes_on_frame(frame_rgb: np.ndarray, result) -> np.ndarray:
    """Draw bounding boxes and labels onto a numpy RGB frame."""
    frame = frame_rgb.copy()
    if result.boxes is None or len(result.boxes) == 0:
        return frame

    for box in result.boxes:
        cls_id = int(box.cls)
        conf   = float(box.conf)
        xyxy   = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = xyxy

        color_bgr = CLASS_COLORS_BGR.get(cls_id, (200, 200, 200))
        color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])

        cv2.rectangle(frame, (x1, y1), (x2, y2), color_rgb, 2)

        label = f"{CLASS_NAMES[cls_id]}  {conf:.0%}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        ly = max(y1 - 8, th + 8)
        cv2.rectangle(frame, (x1, ly - th - 6), (x1 + tw + 6, ly + 2), color_rgb, -1)
        cv2.putText(frame, label, (x1 + 3, ly - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)

    return frame


def extract_detections(result) -> list[dict]:
    """Return list of {cls_id, cls_name, conf, box} from a YOLO result."""
    dets = []
    if result.boxes is None:
        return dets
    for box in result.boxes:
        dets.append({
            "cls_id":   int(box.cls),
            "cls_name": CLASS_NAMES[int(box.cls)],
            "conf":     float(box.conf),
            "box":      box.xyxy[0].cpu().numpy().tolist(),
        })
    return dets


# ──────────────────────────────────────────────────────────────────────────────
# RECOMMENDATION LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def build_recommendation(class_counts: dict) -> dict:
    """
    Given {cls_id: count}, return recommendation payload:
      - percentages per class
      - dominant class (or tie flag)
      - recommendation text
    """
    total = sum(class_counts.values())
    if total == 0:
        return {"type": "none", "total": 0, "percentages": {}, "dominant": None}

    pct = {cls: round(cnt / total * 100, 1) for cls, cnt in class_counts.items() if cnt > 0}

    # Find maximum count(s)
    max_count = max(class_counts.values())
    dominant  = [cls for cls, cnt in class_counts.items() if cnt == max_count]

    is_tie        = len(dominant) > 1
    multi_class   = len([c for c in class_counts.values() if c > 0]) > 1

    return {
        "type":        "tie" if is_tie else "dominant",
        "total":       total,
        "percentages": pct,
        "dominant":    dominant,
        "multi_class": multi_class,
        "is_tie":      is_tie,
    }


def render_recommendation(reco: dict):
    """Render the recommendation section in Streamlit."""
    if reco["total"] == 0:
        st.info("No detections to generate a recommendation.")
        return

    pct  = reco["percentages"]
    total = reco["total"]

    # ── Class distribution bars ────────────────────────────────────────
    st.markdown("#### 📊 Detection Distribution")
    bars_html = ""
    for cls_id in [0, 1, 2]:
        if cls_id not in pct:
            continue
        p     = pct[cls_id]
        color = CLASS_COLORS_HEX[cls_id]
        icon  = CLASS_ICONS[cls_id]
        name  = CLASS_NAMES[cls_id].replace("_", " ").title()
        cnt   = reco.get("counts", {}).get(cls_id, "–")
        bars_html += f"""
        <div class="class-bar-wrap">
          <div class="class-bar-label">
            <span>{icon} {name}</span>
            <span style="font-family:'Space Mono',monospace;color:{color}">
              {p}% &nbsp;({cnt} detections)
            </span>
          </div>
          <div class="class-bar-track">
            <div class="class-bar-fill"
                 style="width:{p}%;background:{color}"></div>
          </div>
        </div>"""
    st.markdown(bars_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Recommendation card(s) ─────────────────────────────────────────
    st.markdown("#### 💡 Recommendations")

    if reco["is_tie"] or reco["multi_class"]:
        # Mixed: show overall mixed advice + individual reco for each class found
        card = MIXED_RECO
        st.markdown(
            f'<div class="reco-card {card["css_class"]}">'
            f'<div class="reco-title">{card["title"]}</div>'
            f'<div class="reco-body">{card["body"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # Then show per-class detail cards
        for cls_id in sorted(pct.keys(), key=lambda c: pct[c], reverse=True):
            r    = RECOMMENDATIONS[cls_id]
            p    = pct[cls_id]
            icon = CLASS_ICONS[cls_id]
            st.markdown(
                f'<div class="reco-card {r["css_class"]}" style="margin-top:12px;">'
                f'<div class="reco-title">'
                f'{icon} {CLASS_NAMES[cls_id].replace("_"," ").title()}'
                f' &nbsp;<span style="font-size:0.8rem;font-weight:400;opacity:0.7">'
                f'({p}% of detections)</span></div>'
                f'<div class="reco-body">{r["body"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        # Single dominant class
        dominant_cls = reco["dominant"][0]
        r = RECOMMENDATIONS[dominant_cls]
        p = pct.get(dominant_cls, 0)
        st.markdown(
            f'<div class="reco-card {r["css_class"]}">'
            f'<div class="reco-title">{r["title"]}'
            f' <span style="font-size:0.8rem;font-weight:400;opacity:0.7">'
            f'({p}% confidence share)</span></div>'
            f'<div class="reco-body">{r["body"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    model_path = st.text_input(
        "Model path (.pt file)",
        value="best.pt",
        help="Path to your trained YOLOv8 weights file",
    )

    conf_thresh = st.slider("Confidence threshold", 0.10, 0.95, 0.25, 0.05)
    iou_thresh  = st.slider("NMS IoU threshold",    0.10, 0.95, 0.45, 0.05)
    imgsz       = st.selectbox("Inference size (px)", [320, 416, 640, 800, 1280], index=2)

    st.markdown("---")
    st.markdown("### 🏷️ Class Legend")
    for cls_id, name in enumerate(CLASS_NAMES):
        color = CLASS_COLORS_HEX[cls_id]
        icon  = CLASS_ICONS[cls_id]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
            f'<div style="width:14px;height:14px;border-radius:3px;background:{color}"></div>'
            f'<span style="font-size:0.85rem">{icon} {name.replace("_"," ").title()}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.72rem;color:#8b949e;text-align:center;">'
        'FAW Detection System · KaraAgro · YOLOv8</p>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🌽 FAW Detection System</h1>
  <p>Fall Armyworm detection from image, video, or live camera feed — 
     powered by YOLOv8 · KaraAgro Dataset</p>
</div>
""", unsafe_allow_html=True)

# Load model
model, model_err = load_model(model_path)
if model_err:
    st.error(f"⚠️ Could not load model: `{model_err}`\n\nUpdate the **Model path** in the sidebar.")
    st.stop()
else:
    st.success(f"✅ Model loaded: `{model_path}`", icon="🤖")


# ──────────────────────────────────────────────────────────────────────────────
# INPUT TABS
# ──────────────────────────────────────────────────────────────────────────────
tab_image, tab_video, tab_webcam = st.tabs(["📷 Image", "🎬 Video", "📹 Webcam / Camera"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — IMAGE
# ══════════════════════════════════════════════════════════════════════════════
with tab_image:
    st.markdown("#### Upload an image of your maize crop")
    uploaded_file = st.file_uploader(
        "Drag & drop or browse",
        type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
        key="img_uploader",
    )

    if uploaded_file:
        col_orig, col_result = st.columns(2, gap="medium")

        pil_img = Image.open(uploaded_file).convert("RGB")

        with col_orig:
            st.markdown("**Original**")
            st.image(pil_img, use_container_width=True)

        with st.spinner("Running detection…"):
            # Preprocess
            preprocessed = preprocess_image(pil_img, target_size=imgsz)
            # Infer on original (model handles resize internally via imgsz param)
            result = run_inference(model, np.array(pil_img), conf_thresh, iou_thresh)

        dets = extract_detections(result)

        # Draw boxes
        annotated = draw_boxes_on_frame(np.array(pil_img), result)

        with col_result:
            st.markdown("**Detections**")
            st.image(annotated, use_container_width=True)

        st.markdown("---")

        # Metrics row
        class_counts = collections.Counter(d["cls_id"] for d in dets)
        total_dets   = len(dets)
        avg_conf     = (sum(d["conf"] for d in dets) / total_dets) if total_dets else 0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f'<div class="metric-card"><div class="val val-blue">{total_dets}</div>'
                        f'<div class="lbl">Total detections</div></div>', unsafe_allow_html=True)
        with col_m2:
            cnt_h = class_counts.get(0, 0)
            st.markdown(f'<div class="metric-card"><div class="val val-green">{cnt_h}</div>'
                        f'<div class="lbl">Healthy</div></div>', unsafe_allow_html=True)
        with col_m3:
            cnt_e = class_counts.get(1, 0)
            st.markdown(f'<div class="metric-card"><div class="val val-amber">{cnt_e}</div>'
                        f'<div class="lbl">Early Stage</div></div>', unsafe_allow_html=True)
        with col_m4:
            cnt_l = class_counts.get(2, 0)
            st.markdown(f'<div class="metric-card"><div class="val val-red">{cnt_l}</div>'
                        f'<div class="lbl">Late Stage</div></div>', unsafe_allow_html=True)

        # Build & render recommendation
        reco = build_recommendation(dict(class_counts))
        reco["counts"] = dict(class_counts)
        render_recommendation(reco)

        # Detection table
        if dets:
            st.markdown("---")
            st.markdown("#### 🗂️ Detection Details")
            import pandas as pd
            df = pd.DataFrame([{
                "#":        i + 1,
                "Class":    CLASS_ICONS[d["cls_id"]] + " " + d["cls_name"].replace("_", " ").title(),
                "Confidence": f"{d['conf']:.1%}",
                "x1": int(d["box"][0]), "y1": int(d["box"][1]),
                "x2": int(d["box"][2]), "y2": int(d["box"][3]),
            } for i, d in enumerate(dets)])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download annotated image
            buf = io.BytesIO()
            Image.fromarray(annotated).save(buf, format="JPEG", quality=92)
            st.download_button(
                "⬇️ Download Annotated Image",
                data=buf.getvalue(),
                file_name="faw_detection_result.jpg",
                mime="image/jpeg",
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VIDEO
# ══════════════════════════════════════════════════════════════════════════════
with tab_video:
    st.markdown("#### Upload a video of your maize field")

    SKIP_FRAMES = st.number_input(
        "Process every N-th frame (1 = all frames, higher = faster)",
        min_value=1, max_value=10, value=2,
        help="Increase to speed up processing on long videos",
    )

    video_file = st.file_uploader(
        "Upload video",
        type=["mp4", "avi", "mov", "mkv", "webm"],
        key="vid_uploader",
    )

    if video_file:
        # Write to temp file for OpenCV
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(video_file.read())
        tfile.flush()

        cap = cv2.VideoCapture(tfile.name)
        fps      = cap.get(cv2.CAP_PROP_FPS) or 25
        total_fr = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w_v      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h_v      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        st.info(f"Video: {w_v}×{h_v}px · {fps:.1f} fps · {total_fr} frames")

        run_btn = st.button("▶️ Run Detection on Video")

        if run_btn:
            stframe      = st.empty()
            progress_bar = st.progress(0, text="Processing frames…")

            # Accumulators
            all_counts   = collections.Counter()
            frame_idx    = 0
            processed    = 0
            start_time   = time.time()

            # Stats placeholders
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            stat_total = stat_col1.empty()
            stat_h     = stat_col2.empty()
            stat_e     = stat_col3.empty()
            stat_l     = stat_col4.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_idx += 1
                progress   = frame_idx / max(total_fr, 1)
                progress_bar.progress(min(progress, 1.0),
                                      text=f"Frame {frame_idx}/{total_fr}")

                # Skip frames for speed
                if frame_idx % SKIP_FRAMES != 0:
                    continue

                processed += 1
                frame_rgb  = preprocess_frame(frame)
                result     = run_inference(model, frame_rgb, conf_thresh, iou_thresh)
                annotated  = draw_boxes_on_frame(frame_rgb, result)
                dets       = extract_detections(result)

                for d in dets:
                    all_counts[d["cls_id"]] += 1

                # Show live frame
                stframe.image(annotated, channels="RGB", use_container_width=True)

                # Live stats
                total_d = sum(all_counts.values())
                stat_total.markdown(
                    f'<div class="metric-card"><div class="val val-blue">{total_d}</div>'
                    f'<div class="lbl">Total dets</div></div>', unsafe_allow_html=True)
                stat_h.markdown(
                    f'<div class="metric-card"><div class="val val-green">{all_counts.get(0,0)}</div>'
                    f'<div class="lbl">Healthy</div></div>', unsafe_allow_html=True)
                stat_e.markdown(
                    f'<div class="metric-card"><div class="val val-amber">{all_counts.get(1,0)}</div>'
                    f'<div class="lbl">Early</div></div>', unsafe_allow_html=True)
                stat_l.markdown(
                    f'<div class="metric-card"><div class="val val-red">{all_counts.get(2,0)}</div>'
                    f'<div class="lbl">Late</div></div>', unsafe_allow_html=True)

            cap.release()
            os.unlink(tfile.name)
            progress_bar.empty()

            elapsed = time.time() - start_time
            st.success(
                f"✅ Processing complete — {processed} frames in {elapsed:.1f}s "
                f"({processed/elapsed:.1f} fps effective)"
            )

            st.markdown("---")
            reco = build_recommendation(dict(all_counts))
            reco["counts"] = dict(all_counts)
            render_recommendation(reco)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEBCAM / CAMERA
# ══════════════════════════════════════════════════════════════════════════════
with tab_webcam:
    st.markdown("#### Live Camera / Webcam Detection")
    st.markdown(
        "_Point your camera at a maize plant. Detections accumulate across the session "
        "to build a recommendation. Press **Stop** to finalise._"
    )

    cam_col1, cam_col2 = st.columns([2, 1])

    with cam_col1:
        camera_img = st.camera_input(
            "📸 Capture frame",
            help="Click the camera button to take a photo for detection",
        )

    with cam_col2:
        st.markdown("**Live Counts (this session)**")
        # Session state for accumulating webcam detections
        if "webcam_counts" not in st.session_state:
            st.session_state.webcam_counts = collections.Counter()

        reset_btn = st.button("🔄 Reset Session Counts")
        if reset_btn:
            st.session_state.webcam_counts = collections.Counter()
            st.rerun()

        total_ws = sum(st.session_state.webcam_counts.values())
        st.markdown(
            f'<div class="metric-card" style="margin-bottom:8px;">'
            f'<div class="val val-blue">{total_ws}</div>'
            f'<div class="lbl">Cumulative detections</div></div>',
            unsafe_allow_html=True,
        )
        for cls_id in [0, 1, 2]:
            cnt   = st.session_state.webcam_counts.get(cls_id, 0)
            color = CLASS_COLORS_HEX[cls_id]
            icon  = CLASS_ICONS[cls_id]
            name  = CLASS_NAMES[cls_id].replace("_", " ").title()
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:6px 10px;background:#161b22;border-radius:6px;'
                f'border-left:3px solid {color};margin-bottom:6px;">'
                f'<span style="font-size:0.82rem">{icon} {name}</span>'
                f'<span style="font-family:Space Mono,monospace;color:{color};font-size:0.82rem">'
                f'{cnt}</span></div>',
                unsafe_allow_html=True,
            )

    if camera_img:
        pil_cam = Image.open(camera_img).convert("RGB")

        with st.spinner("Analysing frame…"):
            result_cam  = run_inference(model, np.array(pil_cam), conf_thresh, iou_thresh)
            annotated_cam = draw_boxes_on_frame(np.array(pil_cam), result_cam)
            dets_cam    = extract_detections(result_cam)

        # Accumulate into session state
        for d in dets_cam:
            st.session_state.webcam_counts[d["cls_id"]] += 1

        # Show annotated frame
        st.image(annotated_cam, caption="Annotated Frame", use_container_width=True)

        # Frame-level counts
        frame_counts = collections.Counter(d["cls_id"] for d in dets_cam)
        st.markdown(
            f"**This frame:** "
            + " · ".join(
                f"{CLASS_ICONS[c]} {CLASS_NAMES[c].replace('_',' ').title()} ×{n}"
                for c, n in sorted(frame_counts.items())
            ) if frame_counts else "**This frame:** No detections"
        )

        st.markdown("---")

        # Recommendation based on accumulated session counts
        if sum(st.session_state.webcam_counts.values()) > 0:
            st.markdown("#### 💡 Recommendation (based on session)")
            reco_cam = build_recommendation(dict(st.session_state.webcam_counts))
            reco_cam["counts"] = dict(st.session_state.webcam_counts)
            render_recommendation(reco_cam)
        else:
            st.info("No detections yet. Capture more frames to generate a recommendation.")

