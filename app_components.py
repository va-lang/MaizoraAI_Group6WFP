"""Reusable UI helpers for AgroSense."""

import base64
import hashlib

import streamlit as st

from app_data import SEVERITY_COLORS


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

        :root {
          --green-900: #0d2818;
          --green-800: #1a3d25;
          --green-700: #1f5c30;
          --green-600: #2a7a40;
          --green-500: #38a357;
          --green-100: #e8fdf0;
          --green-50: #f2fff6;
          --border: #d6ead9;
          --text: #1a2e1d;
          --muted: #6b8f72;
          --red: #d63c3c;
          --orange: #e87c2a;
          --yellow: #f5c842;
        }

        html, body {
          font-family: 'DM Sans', sans-serif;
          color: var(--text);
        }

        .stApp {
          background: #f5f9f6;
          color: var(--text);
        }

        .stApp,
        .stApp p,
        .stApp li,
        .stApp label,
        .stApp span,
        .stApp div,
        .stApp [data-testid="stMarkdownContainer"],
        .stApp [data-testid="stMarkdownContainer"] * {
          color: var(--text);
        }

        header[data-testid="stHeader"] {
          background: linear-gradient(90deg, var(--green-800), var(--green-600));
          border-bottom: 1px solid rgba(255,255,255,.18);
        }

        header[data-testid="stHeader"] * {
          color: #ffffff !important;
        }

        h1, h2, h3 {
          font-family: 'Sora', sans-serif;
          letter-spacing: 0;
          color: var(--text);
        }

        section[data-testid="stSidebar"] {
          background: linear-gradient(180deg, var(--green-900), var(--green-800));
          border-right: 1px solid rgba(255,255,255,.14);
          color: #ffffff !important;
        }

        section[data-testid="stSidebar"] * {
          color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
          background: rgba(255,255,255,.08);
          border: 1px solid rgba(255,255,255,.12);
          border-radius: 10px;
          margin-bottom: 6px;
          padding: 6px 8px;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
          background: rgba(255,255,255,.15);
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
          background: rgba(255,255,255,.15) !important;
          border: 1px solid rgba(255,255,255,.22) !important;
          color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
          background: rgba(255,255,255,.2) !important;
          border-color: rgba(255,255,255,.32) !important;
          color: #ffffff !important;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
          color: rgba(255,255,255,.72);
        }

        section[data-testid="stSidebar"] hr {
          border-color: rgba(255,255,255,.16);
        }

        div[data-testid="stMetric"] {
          background: #ffffff;
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 18px;
          box-shadow: 0 1px 4px rgba(26,46,29,.07);
        }

        .hero {
          background:
            linear-gradient(160deg, rgba(13,40,24,.92), rgba(31,92,48,.76), rgba(56,163,87,.44)),
            radial-gradient(circle at 22% 20%, rgba(128,224,154,.2), transparent 22%),
            linear-gradient(135deg, #1a3d25, #2a7a40);
          border-radius: 22px;
          color: #fff !important;
          padding: 60px 34px;
          text-align: center;
          margin-bottom: 28px;
        }

        .hero h1 {
          font-size: clamp(2rem, 5vw, 3.4rem);
          line-height: 1.14;
          margin-bottom: 14px;
          color: #ffffff !important;
        }

        .hero h1,
        .hero h1 * {
          color: #ffffff !important;
        }

        .hero p {
          color: rgba(255,255,255,.82) !important;
          max-width: 720px;
          margin: 0 auto 26px;
          font-size: 1.05rem;
          line-height: 1.65;
        }

        .tag {
          display: inline-block;
          background: var(--green-100);
          color: var(--green-700) !important;
          border-radius: 20px;
          padding: 5px 14px;
          font-size: .75rem;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .08em;
          margin-bottom: 12px;
        }

        .hero .tag {
          background: rgba(77,201,114,.2);
          border: 1px solid rgba(77,201,114,.4);
          color: #80e09a !important;
        }

        .center-heading {
          text-align: center;
          margin: 36px 0 18px;
        }

        .stMainBlockContainer:has(.login-page-marker) {
          max-width: none;
          padding: 0;
          overflow: hidden;
        }

        .stApp:has(.login-page-marker) {
          height: 100dvh;
          overflow: hidden;
        }

        .stApp:has(.login-page-marker) header[data-testid="stHeader"] {
          display: none;
        }

        .stApp:has(.login-page-marker) section[data-testid="stMain"] {
          height: 100dvh;
          overflow: hidden;
        }

        .login-page-marker + div {
          max-width: 1120px;
          height: 100dvh;
          margin: 0 auto 0 0;
          background: #f7f6f2;
          overflow: hidden;
        }

        .login-page-marker + div > div {
          height: 100%;
          padding: 0 !important;
        }

        .login-brand-panel {
          box-sizing: border-box;
          height: 100dvh;
          min-height: 100dvh;
          padding: 36px 32px 40px;
          background:
            radial-gradient(circle at 5% 8%, rgba(255,255,255,.08) 0 150px, transparent 151px),
            radial-gradient(circle at 90% 95%, rgba(255,255,255,.08) 0 190px, transparent 191px),
            linear-gradient(180deg, var(--green-900), var(--green-800));
          display: flex;
          flex-direction: column;
          color: #ffffff !important;
        }

        .login-brand-panel,
        .login-brand-panel * {
          color: #ffffff !important;
        }

        .login-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 1.15rem;
          font-weight: 700;
        }

        .login-logo-icon {
          width: 38px;
          height: 38px;
          border: 1px solid rgba(255,255,255,.2);
          border-radius: 10px;
          background: rgba(255,255,255,.15);
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }

        .login-brand-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 60px 0 45px;
        }

        .login-eyebrow {
          margin-bottom: 18px;
          color: rgba(255,255,255,.65) !important;
          font-size: .7rem;
          font-weight: 700;
          letter-spacing: .14em;
          text-transform: uppercase;
        }

        .login-brand-content h1 {
          margin-bottom: 20px;
          color: #ffffff !important;
          font-size: clamp(1.9rem, 3vw, 2.35rem);
          line-height: 1.18;
        }

        .login-brand-content > p {
          max-width: 390px;
          margin-bottom: 30px;
          color: rgba(255,255,255,.8) !important;
          font-size: .93rem;
          line-height: 1.75;
        }

        .login-feature {
          display: flex;
          gap: 11px;
          align-items: center;
          margin: 7px 0;
          color: rgba(255,255,255,.9) !important;
          font-size: .875rem;
        }

        .login-feature:first-letter {
          font-weight: 800;
        }

        .login-testimonial {
          border-top: 1px solid rgba(255,255,255,.15);
          padding-top: 22px;
          display: flex;
          flex-direction: column;
          gap: 7px;
          font-size: .82rem;
          line-height: 1.55;
        }

        .login-testimonial em {
          color: rgba(255,255,255,.75) !important;
        }

        .login-testimonial span {
          color: rgba(255,255,255,.55) !important;
        }

        .login-page-marker + div > div:last-child {
          box-sizing: border-box;
          height: 100dvh;
          padding: 48px 36px !important;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        .st-key-login_form_card {
          width: min(100%, 440px);
          margin-left: auto;
          margin-right: auto;
        }

        .login-form-heading {
          text-align: center;
        }

        .login-form-heading h1 {
          margin: 0 0 6px;
          font-size: 1.9rem;
          color: #1a1a1a !important;
        }

        .login-form-heading p {
          margin-bottom: 26px;
          color: #6b7280 !important;
          font-size: .88rem;
        }

        .login-role-label {
          margin-bottom: 9px;
          font-size: .82rem;
          font-weight: 600;
          color: #1a1a1a !important;
        }

        .st-key-login_role_farmer button,
        .st-key-login_role_officer button {
          min-height: 92px;
          padding: 13px 10px;
          white-space: pre-line;
          line-height: 1.35;
          border-radius: 12px;
          font-size: .78rem;
        }

        .st-key-login_role_farmer button p,
        .st-key-login_role_officer button p {
          white-space: pre-line;
        }

        .st-key-login_role_farmer button[kind="primary"],
        .st-key-login_role_officer button[kind="primary"] {
          background: #f0faf3 !important;
          border: 1.5px solid var(--green-600) !important;
          color: var(--green-700) !important;
          box-shadow: 0 0 0 3px rgba(42,122,64,.12);
        }

        .login-password-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin: 2px 0 7px;
          font-size: .82rem;
          font-weight: 600;
        }

        .login-password-row a {
          color: var(--green-600) !important;
          text-decoration: none;
        }

        .login-password-row a:hover {
          color: var(--green-800) !important;
          text-decoration: underline;
        }

        .st-key-login_sign_in button {
          min-height: 48px;
          background: #1db954 !important;
          border-color: #1db954 !important;
          color: #ffffff !important;
          box-shadow: 0 2px 12px rgba(30,185,84,.3);
        }

        .st-key-login_sign_in button:hover {
          background: #17a349 !important;
          border-color: #17a349 !important;
        }

        .login-divider {
          display: flex;
          align-items: center;
          gap: 14px;
          margin: 18px 0 10px;
          color: #6b7280 !important;
          font-size: .78rem;
        }

        .login-divider::before,
        .login-divider::after {
          content: "";
          flex: 1;
          height: 1px;
          background: #e4e4e0;
        }

        .login-footer {
          margin-top: 20px;
          text-align: center;
          color: #6b7280 !important;
          font-size: .82rem;
        }

        .login-footer strong {
          color: var(--green-600) !important;
        }

        @media (max-width: 860px) {
          .login-brand-panel {
            min-height: 430px;
            padding: 30px;
          }

          .login-brand-content {
            padding: 45px 0 30px;
          }

          .login-page-marker + div > div:last-child {
            min-height: auto;
            padding: 42px 28px !important;
          }
        }

        .card {
          background: #ffffff;
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 20px;
          box-shadow: 0 1px 4px rgba(26,46,29,.07);
          height: 100%;
          min-height: 190px;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
        }

        .card,
        .card *,
        .history-card-fixed,
        .history-card-fixed * {
          color: var(--text);
        }

        .feature-title {
          font-family: 'Sora', sans-serif;
          font-size: .98rem;
          font-weight: 700;
          margin-bottom: 6px;
          min-height: 42px;
          display: flex;
          align-items: flex-start;
        }

        .muted {
          color: var(--muted) !important;
          font-size: .88rem;
          line-height: 1.55;
        }

        .history-card-fixed {
          background: #ffffff;
          border: 1px solid var(--border);
          border-radius: 14px;
          overflow: hidden;
          box-shadow: 0 1px 4px rgba(26,46,29,.07);
          height: 380px;
          display: flex;
          flex-direction: column;
          margin-bottom: 8px;
        }

        .history-card-fixed img {
          width: 100%;
          height: 185px;
          object-fit: cover;
          display: block;
          background: var(--green-50);
        }

        .history-card-body {
          padding: 16px;
          flex: 1;
        }

        .alert {
          border-radius: 10px;
          padding: 14px 16px;
          margin: 12px 0 20px;
          font-size: .92rem;
          line-height: 1.5;
        }

        .alert-severe {
          background: #fff0f0;
          border: 1px solid #f5c0c0;
          color: #7a1a1a !important;
        }

        .alert-warning {
          background: #fff6ee;
          border: 1px solid #f5d5b0;
          color: #7a3a00 !important;
        }

        .severity-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border-radius: 20px;
          padding: 5px 12px;
          font-size: .78rem;
          font-weight: 700;
          border: 1px solid currentColor;
        }

        .result-prediction .severity-badge {
          font-size: 1.05rem;
          padding: 8px 16px;
        }

        .leaf-preview {
          min-height: 310px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 18px;
          background: linear-gradient(135deg,#1a3d25 0%,#2a7a40 44%,#4dc972 100%);
          color: white !important;
          font-size: 5rem;
        }

        .stButton > button {
          border-radius: 10px;
          font-weight: 700;
        }

        .hero-actions + div div[data-testid="stButton"] > button {
          min-height: 44px;
          font-size: .95rem;
          border-radius: 10px;
          background: linear-gradient(135deg, #b91c1c, var(--red)) !important;
          border: 1px solid var(--red) !important;
          color: #ffffff !important;
          box-shadow: 0 4px 16px rgba(214,60,60,.24);
        }

        .hero-actions + div div[data-testid="stButton"] > button *,
        .hero-actions + div div[data-testid="stButton"] > button p {
          color: #ffffff !important;
        }

        .st-key-hero_scan_crop button,
        .st-key-hero_scan_crop button *,
        .st-key-hero_scan_crop button p {
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
        }

        .hero-actions + div div[data-testid="stButton"] > button:hover {
          background: linear-gradient(135deg, #991b1b, #b91c1c) !important;
          border-color: #991b1b !important;
          color: #ffffff !important;
        }

        div[data-testid="stDataFrame"] {
          border: 1px solid var(--border);
          border-radius: 14px;
          overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(severity: str, size: str = "normal") -> str:
    color = SEVERITY_COLORS[severity]
    if size == "large":
        return f"<span class='severity-badge' style='color:{color};font-size:1.05rem;padding:8px 16px'>● {severity}</span>"
    return f"<span class='severity-badge' style='color:{color}'>● {severity}</span>"


def alert(kind: str, text: str) -> None:
    css_class = "alert-severe" if kind == "severe" else "alert-warning"
    st.markdown(f"<div class='alert {css_class}'>{text}</div>", unsafe_allow_html=True)


def card(title: str, body: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="card">
          <div style="font-size:1.8rem;margin-bottom:10px">{icon}</div>
          <div class="feature-title">{title}</div>
          <div class="muted">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def image_to_data_url(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{uploaded_file.type};base64,{encoded}"


def demo_prediction(uploaded_file) -> dict:
    """Return a deterministic demo result until a trained model is connected."""
    if uploaded_file is None:
        return {
            "severity": "Severe",
            "confidence": 86,
            "scores": {"Severe": 86.2, "Moderate": 8.4, "Early to Moderate": 4.1, "Healthy": 1.3},
        }

    digest = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    bucket = int(digest[:2], 16) % 4
    severities = ["Healthy", "Early to Moderate", "Moderate", "Severe"]
    severity = severities[bucket]
    confidence = [93, 74, 81, 88][bucket]
    scores = {
        "Healthy": 3.0,
        "Early to Moderate": 5.0,
        "Moderate": 7.0,
        "Severe": 9.0,
    }
    scores[severity] = float(confidence)
    remainder = 100.0 - confidence
    other_labels = [label for label in scores if label != severity]
    for i, label in enumerate(other_labels):
        scores[label] = round(remainder * [0.5, 0.3, 0.2][i], 1)

    return {"severity": severity, "confidence": confidence, "scores": scores}


def ghana_map_svg() -> str:
    return """
    <svg viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:330px">
      <path d="M80 30 L100 20 L140 18 L180 25 L210 35 L225 55 L230 80 L228 110 L232 140 L230 170 L235 200 L238 240 L230 270 L220 300 L200 320 L175 335 L150 340 L125 335 L100 320 L80 300 L65 275 L58 240 L55 200 L52 170 L50 140 L55 110 L52 80 L60 55 Z" fill="#d0f0d8" stroke="#80e09a" stroke-width="2"/>
      <circle cx="150" cy="180" r="28" fill="rgba(214,60,60,.35)" stroke="#d63c3c" stroke-width="1.5"/>
      <circle cx="120" cy="155" r="22" fill="rgba(232,124,42,.3)" stroke="#e87c2a" stroke-width="1.5"/>
      <circle cx="175" cy="210" r="18" fill="rgba(232,124,42,.25)" stroke="#e87c2a" stroke-width="1.5"/>
      <circle cx="140" cy="120" r="14" fill="rgba(245,200,66,.3)" stroke="#f5c842" stroke-width="1.5"/>
      <circle cx="95" cy="200" r="12" fill="rgba(56,163,87,.3)" stroke="#38a357" stroke-width="1.5"/>
      <text x="138" y="185" font-size="9" font-weight="bold" fill="#8a0000" text-anchor="middle">Ashanti</text>
      <text x="110" y="158" font-size="8" fill="#6b3000" text-anchor="middle">B-Ahafo</text>
      <text x="135" y="115" font-size="8" fill="#5a4000" text-anchor="middle">Northern</text>
      <text x="85" y="200" font-size="8" fill="#1a5c30" text-anchor="middle">Western</text>
      <rect x="10" y="310" width="10" height="10" fill="rgba(214,60,60,.5)" rx="2"/>
      <text x="24" y="319" font-size="8" fill="#444">Severe</text>
      <rect x="65" y="310" width="10" height="10" fill="rgba(232,124,42,.5)" rx="2"/>
      <text x="79" y="319" font-size="8" fill="#444">Moderate</text>
      <rect x="135" y="310" width="10" height="10" fill="rgba(245,200,66,.5)" rx="2"/>
      <text x="149" y="319" font-size="8" fill="#444">Early</text>
      <rect x="185" y="310" width="10" height="10" fill="rgba(56,163,87,.5)" rx="2"/>
      <text x="199" y="319" font-size="8" fill="#444">Healthy</text>
    </svg>
    """
