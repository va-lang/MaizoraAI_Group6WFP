import time

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
    HISTORY_DATA,
    RECENT_SCANS,
    REGIONAL_ACTIVITY,
    RESULT_TEXT,
    SEVERITY_COLORS,
    SEVERITY_RECOMMENDATIONS,
    SEVERITY_RECOMMENDATIONS_TWI,
    TREND_DATA,
)


st.set_page_config(
    page_title="AgroSense - AI Maize Pest Detection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


def init_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "last_upload" not in st.session_state:
        st.session_state.last_upload = None
    if "prediction" not in st.session_state:
        st.session_state.prediction = demo_prediction(None)


def goto(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def sidebar_nav() -> None:
    with st.sidebar:
        st.markdown("## 🌱 AgroSense")
        st.caption("AI Fall Armyworm detection for Ghanaian maize farms")
        page = st.radio(
            "Navigation",
            ["Home", "Scan Crop", "Results", "Dashboard", "History"],
            index=["Home", "Scan Crop", "Results", "Dashboard", "History"].index(st.session_state.page),
        )
        st.session_state.page = page
        st.divider()
        st.markdown("**Tools**")
        st.write("🔔 Alerts: 3")
        st.write("🗺️ Outbreak Map")
        st.write("📘 Pesticide Guide")
        st.divider()
        st.caption("Demo account")
        st.write("Akosua Kumi")
        st.caption("Ejura District, Ashanti")


def home_page() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="tag">AgroSense - AI Maize Pest Detection</div>
          <h1>AI-Powered Fall Armyworm Detection for Ghanaian Farmers</h1>
          <p>Upload a maize leaf photo and get instant infestation severity predictions, actionable recommendations, and real-time outbreak monitoring from your phone.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-actions">', unsafe_allow_html=True)
    hero_cta1, hero_cta2 = st.columns(2)
    if hero_cta1.button("Scan Crop", type="primary", use_container_width=True, key="hero_scan_crop"):
        goto("Scan Crop")
    if hero_cta2.button("View Dashboard", type="primary", use_container_width=True, key="hero_view_dashboard"):
        goto("Dashboard")
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
    alert("warning", "<strong>Outbreak Alert - Brong-Ahafo Region:</strong> 12 severe infestations reported in the last 24 hours.")

    left, right = st.columns([1.35, 1])
    with left:
        uploaded_file = st.file_uploader(
            "Upload maize leaf image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Use a clear image where the leaf fills most of the frame.",
        )
        camera_image = st.camera_input("Take maize leaf photo")
        selected_image = camera_image or uploaded_file
        if selected_image:
            st.session_state.last_upload = selected_image
            st.image(selected_image, caption="Selected maize leaf image", use_container_width=True)

        location = st.text_input("Location", "Ashanti Region, Ejura")
        crop_stage = st.selectbox("Crop stage", ["Seedling", "Vegetative (V6)", "Tasseling", "Silking"])
        farm_size = st.number_input("Farm size in acres", min_value=0.1, value=2.3, step=0.1)

        if st.button("Analyze Crop", type="primary", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            for value, label in [
                (25, "Image uploaded and validated"),
                (50, "Preprocessing leaf features"),
                (75, "Running CNN inference"),
                (100, "Generating recommendations"),
            ]:
                status.write(label)
                progress.progress(value)
                time.sleep(0.25)
            st.session_state.prediction = demo_prediction(selected_image)
            st.session_state.scan_meta = {
                "location": location,
                "crop_stage": crop_stage,
                "farm_size": farm_size,
            }
            goto("Results")

    with right:
        st.subheader("Photo Tips")
        card("Good Lighting", "Take photos in natural daylight. Avoid harsh shadows on the leaf.", "☀️")
        card("Fill the Frame", "The leaf should fill at least 70% of the photo for best accuracy.", "🔎")
        card("Show Damage Areas", "Focus on chewing marks, frass, or discoloration.", "👁️")

        st.subheader("Recent Community Scans")
        for item in RECENT_SCANS:
            st.markdown(
                f"**{item['farmer']}** - {item['region']}  \n"
                f"<span class='muted'>{item['time']}</span> {severity_badge(item['severity'])}",
                unsafe_allow_html=True,
            )


def results_page() -> None:
    prediction = st.session_state.prediction
    severity = prediction["severity"]
    confidence = prediction["confidence"]
    _, lang_col = st.columns([0.82, 0.18])
    with lang_col:
        language = st.selectbox("Language", ["English", "Twi"])
    text = RESULT_TEXT[language]
    recommendations = (
        SEVERITY_RECOMMENDATIONS_TWI[severity]
        if language == "Twi"
        else SEVERITY_RECOMMENDATIONS[severity]
    )
    meta = st.session_state.get(
        "scan_meta",
        {"location": "Ashanti Region, Ejura", "crop_stage": "Vegetative (V6)", "farm_size": 2.3},
    )

    st.title(text["title"])
    st.caption(text["caption"])
    if severity == "Severe":
        alert("severe", text["severe_alert"])

    left, right = st.columns([1, 1.6])
    with left:
        if st.session_state.last_upload is not None:
            st.image(image_to_data_url(st.session_state.last_upload), caption=text["image_caption"], use_container_width=True)
        else:
            st.markdown("<div class='leaf-preview'>🌽</div>", unsafe_allow_html=True)
        st.markdown(f"### {text['metadata']}")
        st.write(f"**{text['location']}:** {meta['location']}")
        st.write(f"**{text['crop_stage']}:** {meta['crop_stage']}")
        st.write(f"**{text['farm_size']}:** {meta['farm_size']} acres")
        st.write(f"**{text['logged_by']}:** Akosua Kumi")

    with right:
        st.markdown(f"### {text['prediction']}: {severity_badge(severity)}", unsafe_allow_html=True)
        st.metric(text["confidence"], f"{confidence}%")
        scores = pd.DataFrame(
            {"Severity": list(prediction["scores"].keys()), "Score": list(prediction["scores"].values())}
        ).set_index("Severity")
        st.bar_chart(scores, color=SEVERITY_COLORS.get(severity, "#38a357"))

        st.markdown(f"### {text['recommended_action']}")
        for recommendation in recommendations:
            st.write(f"- {recommendation}")

        c1, c2 = st.columns(2)
        if c1.button(text["scan_another"], type="primary", use_container_width=True):
            goto("Scan Crop")
        c2.download_button(
            text["download"],
            data=f"AgroSense Report\nSeverity: {severity}\nConfidence: {confidence}%\nLocation: {meta['location']}\n",
            file_name="agrosense_report.txt",
            use_container_width=True,
        )


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
    st.dataframe(pd.DataFrame(DISTRICT_REPORTS), use_container_width=True, hide_index=True)


def history_page() -> None:
    st.title("Scan History")
    st.caption("Akosua Kumi - Ejura District, Ashanti - 47 total scans")

    severity_filter = st.segmented_control(
        "Filter by severity",
        ["All", "Severe", "Moderate", "Early", "Healthy"],
        default="All",
    )
    rows = HISTORY_DATA
    if severity_filter != "All":
        rows = [row for row in HISTORY_DATA if row["severity"] == severity_filter]

    for row_set in [rows[i : i + 4] for i in range(0, len(rows), 4)]:
        cols = st.columns(4)
        for col, item in zip(cols, row_set):
            with col:
                st.markdown(
                    f"""
                    <div class="card">
                      <div style="font-size:2.4rem">🌽</div>
                      <div class="feature-title">{item['farm']}</div>
                      <div class="muted">{item['date']}</div>
                      <div class="muted">{item['location']}</div>
                      <div style="margin-top:10px">{severity_badge(item['severity'])}</div>
                      <div style="margin-top:10px;font-weight:700;color:{SEVERITY_COLORS[item['severity']]}">{item['confidence']}% confidence</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def main() -> None:
    init_state()
    sidebar_nav()
    pages = {
        "Home": home_page,
        "Scan Crop": scan_page,
        "Results": results_page,
        "Dashboard": dashboard_page,
        "History": history_page,
    }
    pages[st.session_state.page]()


if __name__ == "__main__":
    main()
