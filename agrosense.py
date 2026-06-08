import time
import tempfile
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from app_components import (
    alert,
    apply_theme,
    card,
    demo_prediction,
    ghana_map_svg,
    image_to_data_url,
    severity_badge,
)
from app_data import (
    DISTRICT_REPORTS,
    REGIONAL_ACTIVITY,
    RESULT_TEXT,
    SEVERITY_COLORS,
    SEVERITY_RECOMMENDATIONS,
    SEVERITY_RECOMMENDATIONS_TWI,
    TREND_DATA,
)
from model_service import predict_leaf_image, predict_video
from storage_service import clear_scan_history, format_scan_time, get_scan, get_scans, init_db, save_scan


st.set_page_config(
    page_title="MaizeSecure - AI Maize Pest Detection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


def init_state() -> None:
    init_db()
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "last_upload" not in st.session_state:
        st.session_state.last_upload = None
    if "prediction" not in st.session_state:
        st.session_state.prediction = demo_prediction(None)
    if "selected_scan_id" not in st.session_state:
        st.session_state.selected_scan_id = None
    if "confirm_clear_history" not in st.session_state:
        st.session_state.confirm_clear_history = False


def goto(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def choose_profile(profile: str) -> None:
    st.session_state.profile = profile
    st.session_state.page = "Home"
    st.rerun()


def build_excel_report(severity: str, confidence: int, recommendations: list[str]) -> bytes:
    output = BytesIO()
    summary = pd.DataFrame(
        [
            {"Field": "Severity", "Value": severity},
            {"Field": "Confidence", "Value": f"{confidence}%"},
        ]
    )
    actions = pd.DataFrame({"Recommended Action": recommendations})

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        actions.to_excel(writer, sheet_name="Recommendations", index=False)

    return output.getvalue()


def recommendation_disclaimer() -> None:
    st.caption(
        "Disclaimer: These recommendations are deliberately conservative, high-level action guides. "
        "They do not constitute a full agronomic prescription, and explicitly acknowledge the "
        "irreplaceable value of expert extension guidance for field-level management decisions."
    )


def bytes_to_data_url(data: bytes, mime_type: str) -> str:
    import base64

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


@dataclass
class InMemoryUpload:
    data: bytes
    type: str = "image/jpeg"
    name: str = "video_frame.jpg"

    def getvalue(self) -> bytes:
        return self.data


def extract_video_frame(video_file, frame_position: int) -> tuple[InMemoryUpload | None, str | None]:
    try:
        import cv2
    except ImportError:
        return None, "Video support requires opencv-python-headless. Install requirements and restart the app."

    suffix = Path(video_file.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
        temp_video.write(video_file.getvalue())
        temp_path = Path(temp_video.name)

    try:
        capture = cv2.VideoCapture(str(temp_path))
        if not capture.isOpened():
            return None, "Could not read the uploaded video."

        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if frame_count > 1:
            target_frame = int((frame_position / 100) * (frame_count - 1))
            capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

        ok, frame = capture.read()
        capture.release()
        if not ok:
            return None, "Could not extract a frame from the uploaded video."

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return None, "Could not convert the video frame into an image."

        return InMemoryUpload(encoded.tobytes()), None
    finally:
        temp_path.unlink(missing_ok=True)


def sidebar_nav() -> None:
    with st.sidebar:
        st.markdown("## 🌱 MaizeSecure")
        st.caption("AI Fall Armyworm detection for Ghanaian maize farms")
        st.markdown(f"**Profile:** {st.session_state.profile}")
        if st.button("Switch Profile", width="stretch"):
            st.session_state.profile = None
            st.rerun()
        st.divider()
        page = st.radio(
            "Navigation",
            ["Home", "Scan Crop", "Results", "History"],
            index=["Home", "Scan Crop", "Results", "History"].index(st.session_state.page),
        )
        st.session_state.page = page
        st.divider()
        st.markdown("**Tools**")
        st.write("🔔 Alerts: 3")
        st.write("🗺️ Outbreak Map")
        st.write("📘 Pesticide Guide")
        st.divider()
        st.caption("Profile")
        st.write("Akosua Kumi")
        st.caption("Farmer - Ejura District, Ashanti")


def profile_page() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="tag">MaizeSecure Profiles</div>
          <h1>Select Your Profile</h1>
          <p>Choose Farmer to access the current maize crop scanning workflow. Extension Officer tools will be added later.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    farmer_col, officer_col = st.columns(2)
    with farmer_col:
        st.markdown(
            """
            <div class="card">
              <div style="font-size:2.4rem">👨‍🌾</div>
              <div class="feature-title">Farmer</div>
              <div class="muted">Scan maize leaves, view AI results, download reports, and check scan history.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Continue as Farmer", type="primary", width="stretch"):
            choose_profile("Farmer")
    with officer_col:
        st.markdown(
            """
            <div class="card">
              <div style="font-size:2.4rem">🧑‍💼</div>
              <div class="feature-title">Extension Officer</div>
              <div class="muted">Regional monitoring and farmer support tools will be developed in the next phase.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign in as an Extension Officer", width="stretch"):
            choose_profile("Extension Officer")


def extension_officer_page() -> None:
    with st.sidebar:
        st.markdown("## 🌱 MaizeSecure")
        st.markdown("**Profile:** Extension Officer")
        if st.button("Switch Profile", width="stretch"):
            st.session_state.profile = None
            st.rerun()

    st.markdown(
        """
        <div class="hero">
          <div class="tag">Extension Officer</div>
          <h1>Officer Workspace Coming Later</h1>
          <p>This profile is reserved for future regional monitoring, farmer case review, and outbreak response workflows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Switch to Farmer Profile", type="primary"):
        choose_profile("Farmer")


def home_page() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="tag">MaizeSecure - AI Maize Pest Detection</div>
          <h1>AI-Powered Fall Armyworm Detection for Ghanaian Farmers</h1>
          <p>Upload a maize leaf photo and get instant infestation severity predictions, actionable recommendations, and real-time outbreak monitoring from your phone.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-actions">', unsafe_allow_html=True)
    _, hero_cta, _ = st.columns([1, 0.35, 1])
    if hero_cta.button("📷 Scan Crop", type="primary", width="stretch", key="hero_scan_crop"):
        goto("Scan Crop")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<h2 class='center-heading'>From Leaf to Action in 4 Simple Steps</h2>",
        unsafe_allow_html=True,
    )
    steps = st.columns(4)
    with steps[0]:
        card("1. Upload Leaf Image", "Take a photo of your maize leaf or upload from gallery.", "📷")
    with steps[1]:
        card("2. AI Analysis", "The model checks leaf texture, feeding marks, and discoloration.", "🤖")
    with steps[2]:
        card("3. Get Results", "Receive severity rating from Healthy to Severe with confidence score.", "📊")
    with steps[3]:
        card("4. Take Action", "Follow treatment advice and escalate severe cases to extension officers.", "✅")

    st.markdown(
        "<h2 class='center-heading'>Platform Features</h2>",
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns(3)
    with f1:
        card("AI Detection Engine", "Classifies Fall Armyworm severity levels from maize leaf images.", "🧠")
        card("Smart Alerts", "Notifies farmers about severe outbreaks in their district.", "🔔")
    with f2:
        card("Real-Time Monitoring", "Tracks outbreak trends across Ghana's 16 regions.", "🗺️")
        card("Treatment Guidance", "Provides context-specific pesticide and monitoring recommendations.", "🧪")
    with f3:
        card("Offline-Ready Workflow", "Designed for field use with later syncing when internet returns.", "📶")
        card("Farmer History", "Keeps previous scans organized by date, farm block, and severity.", "👥")


def scan_page() -> None:
    st.title("Scan Your Maize Crop")
    st.caption("Upload a clear photo of a maize leaf to detect Fall Armyworm infestation severity.")

    left, right = st.columns([1.35, 1])
    with left:
        input_mode = st.segmented_control(
            "Input source",
            ["Image", "Camera", "Video"],
            default="Image",
        )
        selected_image = None
        video_file = None
        video_sample_count = 8

        if input_mode == "Image":
            uploaded_file = st.file_uploader(
                "Upload maize leaf image",
                type=["jpg", "jpeg", "png", "webp"],
                help="Use a clear image where the leaf fills most of the frame.",
            )
            selected_image = uploaded_file
        elif input_mode == "Camera":
            selected_image = st.camera_input("Take maize leaf photo")
        else:
            video_file = st.file_uploader(
                "Upload maize crop video",
                type=["mp4", "mov", "avi", "m4v"],
                help="Upload a short video. The AI will sample frames across the recording.",
            )
            if video_file:
                st.video(video_file)
                video_sample_count = st.slider(
                    "Frames to analyze",
                    min_value=3,
                    max_value=15,
                    value=8,
                    help="More frames provide broader coverage but take longer to process.",
                )
                frame_position = st.slider(
                    "Preview frame position",
                    min_value=0,
                    max_value=100,
                    value=50,
                    help="This only controls the preview. Analysis samples the full video.",
                )
                selected_image, video_error = extract_video_frame(video_file, frame_position)
                if video_error:
                    st.error(video_error)

        if selected_image:
            st.session_state.last_upload = selected_image
            preview_image = selected_image.getvalue() if isinstance(selected_image, InMemoryUpload) else selected_image
            st.image(preview_image, caption="Selected maize leaf image", width="stretch")

        if st.button("Analyze Crop", type="primary", width="stretch"):
            if selected_image is None:
                st.warning("Upload, capture, or extract a maize leaf image before analysis.")
                return
            progress = st.progress(0)
            status = st.empty()
            for value, label in [
                (25, "Image uploaded and validated"),
                (50, "Preprocessing leaf features"),
                (75, "Running AI inference"),
                (100, "Generating recommendations"),
            ]:
                status.write(label)
                progress.progress(value)
                time.sleep(0.25)

            if input_mode == "Video":
                prediction, representative_frame = predict_video(
                    video_file,
                    sample_count=video_sample_count,
                )
                if representative_frame is not None:
                    selected_image = InMemoryUpload(
                        representative_frame,
                        name="video_representative_frame.jpg",
                    )
                    st.session_state.last_upload = selected_image
            else:
                prediction = predict_leaf_image(selected_image)

            st.session_state.prediction = prediction
            scan_id = save_scan(selected_image, prediction)
            st.session_state.last_scan_id = scan_id
            st.session_state.scan_meta = {
                "location": "Ashanti Region, Ejura",
                "crop_stage": "Vegetative (V6)",
                "farm_size": 2.3,
            }
            goto("Results")

    with right:
        st.subheader("Photo Tips")
        card("Good Lighting", "Take photos in natural daylight. Avoid harsh shadows on the leaf.", "☀️")
        card("Fill the Frame", "The leaf should fill at least 70% of the photo for best accuracy.", "🔎")
        card("Show Damage Areas", "Focus on chewing marks, frass, or discoloration.", "👁️")


def results_page() -> None:
    prediction = st.session_state.prediction
    severity = prediction["severity"]
    confidence = prediction["confidence"]
    _, lang_col = st.columns([0.82, 0.18])
    with lang_col:
        language = st.selectbox("Language", ["English", "Twi"])
    text = RESULT_TEXT[language]
    st.title(text["title"])
    st.caption(text["caption"])

    if prediction.get("source") in {"error", "no_detection"}:
        if prediction.get("source") == "no_detection":
            st.warning("The model could not detect a maize leaf condition in this image.")
            st.info("Try a clearer maize leaf photo with the leaf filling most of the frame.")
        else:
            st.error("The real maize model could not run in this environment.")
            st.caption(f"Model error: {prediction.get('error', 'Unknown model error')}")
        if st.button(text["scan_another"], type="primary"):
            goto("Scan Crop")
        return

    recommendations = (
        SEVERITY_RECOMMENDATIONS_TWI[severity]
        if language == "Twi"
        else SEVERITY_RECOMMENDATIONS[severity]
    )

    if severity == "Severe":
        alert("severe", text["severe_alert"])

    left, right = st.columns([1, 1.6])
    with left:
        if prediction.get("annotated_image"):
            st.image(
                prediction["annotated_image"],
                caption="AI detections",
                width="stretch",
            )
        elif st.session_state.last_upload is not None:
            st.image(image_to_data_url(st.session_state.last_upload), caption=text["image_caption"], width="stretch")
        else:
            st.markdown("<div class='leaf-preview'>🌽</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            f"<div class='result-prediction'><h3>{text['prediction']}: {severity_badge(severity)}</h3></div>",
            unsafe_allow_html=True,
        )
        st.metric(text["confidence"], f"{confidence}%")
        if prediction.get("frames_processed"):
            st.caption(
                f"Analyzed {prediction['frames_processed']} sampled video frames. "
                "Counts describe frame-level detections, not unique plants."
            )

        st.markdown(f"### {text['recommended_action']}")
        recommendation_disclaimer()
        for recommendation in recommendations:
            st.write(f"- {recommendation}")

        c1, c2 = st.columns(2)
        if c1.button(text["scan_another"], type="primary", width="stretch"):
            goto("Scan Crop")
        c2.download_button(
            text["download"],
            data=build_excel_report(severity, confidence, recommendations),
            file_name="MaizeSecure_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    class_counts = prediction.get("class_counts", {})
    if class_counts:
        st.markdown("### Detection Summary")
        summary_columns = st.columns(3)
        for column, label in zip(
            summary_columns,
            ["Healthy", "Early to Moderate", "Severe"],
        ):
            column.metric(label, class_counts.get(label, 0))

    detections = prediction.get("detections", [])
    if detections:
        detail_rows = []
        for index, detection in enumerate(detections[:100], start=1):
            row = {
                "#": index,
                "Severity": detection["severity"],
                "Confidence": f"{detection['confidence']:.1f}%",
            }
            if "frame" in detection:
                row["Video Frame"] = detection["frame"]
            detail_rows.append(row)

        with st.expander("View detection details"):
            st.dataframe(pd.DataFrame(detail_rows), width="stretch", hide_index=True)
            if len(detections) > 100:
                st.caption(f"Showing the first 100 of {len(detections)} detections.")


def dashboard_page() -> None:
    st.title("National Outbreak Dashboard")
    st.caption("Real-time monitoring across all 16 regions - demo data")
    alert("severe", "<strong>Active Alert:</strong> Severe FAW outbreak spreading across Brong-Ahafo and Ashanti regions. MoFA intervention teams deployed.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scans", "12,840", "18.2% this week")
    c2.metric("Severe Outbreaks", "348", "22 new today")
    c3.metric("Regions Monitored", "16", "Full coverage")
    c4.metric("Active Farmers", "3,241", "142 this week")

    trend_df = pd.DataFrame(TREND_DATA).set_index("Date")
    regional_df = pd.DataFrame(REGIONAL_ACTIVITY).set_index("Region")
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Severity Trend - Last 30 Days")
        st.line_chart(trend_df)
    with right:
        st.subheader("Scan Distribution")
        distribution = pd.DataFrame(
            {"Severity": ["Healthy", "Early", "Moderate", "Severe"], "Percent": [38, 24, 22, 16]}
        ).set_index("Severity")
        st.bar_chart(distribution)

    map_col, bar_col = st.columns([1.2, 1])
    with map_col:
        st.subheader("Ghana Outbreak Heatmap")
        st.markdown(f"<div class='card'>{ghana_map_svg()}</div>", unsafe_allow_html=True)
    with bar_col:
        st.subheader("Regional Scan Activity")
        st.bar_chart(regional_df)

    st.subheader("District Outbreak Report")
    st.dataframe(pd.DataFrame(DISTRICT_REPORTS), width="stretch", hide_index=True)


def history_page() -> None:
    st.title("Scan History")
    st.caption("Akosua Kumi - Ejura District, Ashanti")

    severity_col, date_col, clear_col = st.columns([1.35, 1.35, 0.8])
    with severity_col:
        severity_filter = st.segmented_control(
            "Filter by severity",
            ["All", "Early to Moderate", "Healthy", "Severe"],
            default="All",
        )
    with date_col:
        date_filter = st.segmented_control(
            "Filter by date",
            ["All dates", "Today", "Date range"],
            default="All dates",
        )
    with clear_col:
        st.write("")
        st.write("")
        if st.button("Clear History", width="stretch"):
            st.session_state.confirm_clear_history = True

    start_date = None
    end_date = None
    if date_filter == "Today":
        start_date = date.today()
        end_date = date.today()
    elif date_filter == "Date range":
        start_date, end_date = st.date_input(
            "Choose date range",
            value=(date.today(), date.today()),
        )

    if st.session_state.confirm_clear_history:
        st.warning("This will permanently delete all saved scan history from this app.")
        confirm_col, cancel_col = st.columns([0.35, 0.65])
        if confirm_col.button("Yes, clear all", type="primary"):
            clear_scan_history()
            st.session_state.selected_scan_id = None
            st.session_state.confirm_clear_history = False
            st.success("Scan history cleared.")
            st.rerun()
        if cancel_col.button("Cancel"):
            st.session_state.confirm_clear_history = False
            st.rerun()

    rows = get_scans(severity_filter, start_date, end_date)
    if not rows:
        st.info("No scans match the selected filters.")
        return

    if st.session_state.selected_scan_id:
        selected_scan = get_scan(st.session_state.selected_scan_id)
        if selected_scan:
            st.subheader(f"Scan #{selected_scan['id']} Details")
            detail_image, detail_info = st.columns([1.1, 1])
            with detail_image:
                st.image(selected_scan["image"], caption="Full scan image", width="stretch")
            with detail_info:
                st.markdown(severity_badge(selected_scan["severity"]), unsafe_allow_html=True)
                st.metric("Confidence", f"{selected_scan['confidence']}%")
                st.write(f"**Logged:** {format_scan_time(selected_scan['scanned_at'])}")
                st.write(f"**Source:** {selected_scan['source']}")
                st.markdown("### Recommended Action")
                recommendation_disclaimer()
                for recommendation in SEVERITY_RECOMMENDATIONS[selected_scan["severity"]]:
                    st.write(f"- {recommendation}")
                if st.button("Close Details"):
                    st.session_state.selected_scan_id = None
                    st.rerun()

    for row_set in [rows[i : i + 4] for i in range(0, len(rows), 4)]:
        cols = st.columns(4)
        for col, item in zip(cols, row_set):
            with col:
                image_url = bytes_to_data_url(item["image"], item["image_type"])
                st.markdown(
                    f"""
                    <div class="history-card-fixed">
                      <img src="{image_url}" alt="Scan #{item['id']}">
                      <div class="history-card-body">
                        <div class="feature-title">Scan #{item['id']}</div>
                        <div class="muted">{format_scan_time(item['scanned_at'])}</div>
                        <div style="margin-top:10px">{severity_badge(item['severity'])}</div>
                        <div style="margin-top:8px;font-weight:700;color:{SEVERITY_COLORS[item['severity']]}">{item['confidence']}% confidence</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("View Details", key=f"history_scan_{item['id']}", width="stretch"):
                    st.session_state.selected_scan_id = item["id"]
                    st.rerun()


def main() -> None:
    init_state()
    if st.session_state.profile is None:
        profile_page()
        return

    if st.session_state.profile == "Extension Officer":
        extension_officer_page()
        return

    sidebar_nav()
    pages = {
        "Home": home_page,
        "Scan Crop": scan_page,
        "Results": results_page,
        "History": history_page,
    }
    pages[st.session_state.page]()


if __name__ == "__main__":
    main()
