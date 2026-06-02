import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration
import av

# -----------------------------------------------------------------------------
# APPLICATION SETUP & LOGIC
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Fall Armyworm AI Advisor", layout="wide", page_icon="🌽")

st.title("🌽 Fall Armyworm Intelligent Advisor")
st.write("Detect infestation levels in real-time and receive immediate agricultural management recommendations.")

# Load the TFLite model safely
@st.cache_resource
def load_model():
    # Points to your exported TFLite folder or file
    return YOLO("best_saved_model")

try:
    model = load_model()
except Exception as e:
    st.error(f"Model loading failed. Ensure 'best_saved_model' exists. Error: {e}")
    st.stop()

# Define management recommendation lookup
RECOMMENDATIONS = {
    "healthy": {
        "title": "✅ Healthy Field Condition",
        "color": "green",
        "action": "No immediate chemical intervention required. Continue routine scouting twice a week. Maintain field sanitation and weed management to eliminate alternative pest hosts."
    },
    "early_to_moderate": {
        "title": "⚠️ Early to Moderate Infestation",
        "color": "orange",
        "action": "Action required to prevent spreading. Apply target-specific bio-pesticides (e.g., Bacillus thuringiensis / Bt) or neem-based botanical sprays. Check the whorls of adjacent plants manually."
    },
    "severe": {
        "title": "🚨 Severe Infestation Detected",
        "color": "red",
        "action": "Immediate emergency intervention needed. Apply recommended chemical insecticides (e.g., Emamectin benzoate, Spinetoram, or Chlorantraniliprole) directly into the plant whorls. Coordinate with local agricultural extension officers immediately."
    }
}

def generate_report(detected_classes):
    """Generates an aggregated advisory report based on all unique classes found."""
    if not detected_classes:
        st.info("No Fall Armyworm signatures or corn plants detected in the current view.")
        return

    st.subheader("📋 Field Analysis & Advisory Report")
    
    # Prioritize severe warnings by showing them first
    priority_order = ["severe", "early_to_moderate", "healthy"]
    
    for status in priority_order:
        if status in detected_classes:
            rec = RECOMMENDATIONS[status]
            st.markdown(
                f"""
                <div style="border-left: 5px solid {rec['color']}; padding: 10px; margin-bottom: 10px; background-color: rgba(0,0,0,0.05); border-radius: 4px;">
                    <strong style="color: {rec['color']}; font-size: 1.1em;">{rec['title']}</strong><br/>
                    <p style="margin-top: 5px; margin-bottom: 0;">{rec['action']}</p>
                </div>
                """, 
                unsafe_style_allowed=True
            )

# -----------------------------------------------------------------------------
# SIDEBAR INTERFACE
# -----------------------------------------------------------------------------
source_radio = st.sidebar.radio("Choose Detection Mode", ["Static Photo", "Upload Video File", "Live Phone/Webcam"])
confidence_threshold = st.sidebar.slider("AI Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

# -----------------------------------------------------------------------------
# MODE 1: STATIC PHOTO PROCESSING
# -----------------------------------------------------------------------------
if source_radio == "Static Photo":
    uploaded_file = st.file_uploader("Upload a field photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        opencv_img = cv2.imdecode(file_bytes, 1)
        
        # Run inference
        results = model.predict(opencv_img, conf=confidence_threshold)
        annotated_img = results[0].plot()
        
        # Extract unique classes detected in this image
        detected_ids = results[0].boxes.cls.cpu().numpy().astype(int)
        class_names = results[0].names
        unique_detections = set([class_names[cid] for cid in detected_ids])
        
        # UI Display Split
        col1, col2 = st.columns(2)
        with col1:
            st.image(cv2.cvtColor(opencv_img, cv2.COLOR_BGR2RGB), caption="Uploaded Field Photo", use_container_width=True)
        with col2:
            st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption="AI Detections", use_container_width=True)
            
        # Display aggregate recommendations below images
        generate_report(unique_detections)

# -----------------------------------------------------------------------------
# MODE 2: UPLOADED VIDEO PROCESSING
# -----------------------------------------------------------------------------
elif source_radio == "Upload Video File":
    uploaded_video = st.file_uploader("Upload a field video clip...", type=["mp4", "avi", "mov"])
    
    if uploaded_video is not None:
        with open("temp_field_video.mp4", "wb") as f:
            f.write(uploaded_video.read())
            
        cap = cv2.VideoCapture("temp_field_video.mp4")
        st_frame = st.empty()
        stop_btn = st.button("Stop Video Playback")
        
        # Keep track of everything seen throughout the entire video
        all_video_detections = set()
        
        while cap.isOpened() and not stop_btn:
            ret, frame = cap.read()
            if not ret:
                break
                
            results = model.predict(frame, conf=confidence_threshold, verbose=False)
            annotated_frame = results[0].plot()
            
            # Record detections from this specific frame
            detected_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            class_names = results[0].names
            for cid in detected_ids:
                all_video_detections.add(class_names[cid])
            
            st_frame.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            
        cap.release()
        st.success("Video processing complete.")
        
        # Generate summary report for the entire video clip
        generate_report(all_video_detections)

# -----------------------------------------------------------------------------
# MODE 3: LIVE CLOUD-COMPATIBLE WEBCAM / PHONE CAMERA
# -----------------------------------------------------------------------------
elif source_radio == "Live Phone/Webcam":
    st.info("Allow camera access. This engine compiles real-time feed frames natively across cloud and mobile links.")
    
    # Global state dictionary hack to keep track of active video stream detections across execution reruns
    if "live_detections" not in st.session_state:
        st.session_state.live_detections = set()

    # Clear button to reset live history counters
    if st.button("Reset Live Report Logs"):
        st.session_state.live_detections = False
        st.session_state.live_detections = set()
        st.rerun()

    # WebRTC Video Processing Engine Class
    class VideoProcessor:
        def recv_into_frame(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            
            # Run inference directly on the incoming live frame stream 
            results = model.predict(img, conf=confidence_threshold, verbose=False)
            annotated_img = results[0].plot()
            
            # Extract classes safely inside the threading frame pipeline loop
            detected_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            class_names = results[0].names
            for cid in detected_ids:
                st.session_state.live_detections.add(class_names[cid])
                
            # Return processed annotated matrix box array back to screen
            return av.VideoFrame.from_ndarray(annotated_img, format="bgr24")

    # Start the WebRTC Client Link Streamer Hook 
    ctx = webrtc_streamer(
        key="fall-armyworm-streamer",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:://google.com"]}]}),
        video_frame_callback=VideoProcessor().recv_into_frame,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Display the rolling aggregate report directly beneath the active camera component
    if ctx.state.playing:
        generate_report(st.session_state.live_detections)
