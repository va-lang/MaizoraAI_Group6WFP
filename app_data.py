"""Static demo data for the AgroSense Streamlit prototype."""

SEVERITY_COLORS = {
    "Healthy": "#38a357",
    "Early": "#f5c842",
    "Moderate": "#e87c2a",
    "Severe": "#d63c3c",
}

SEVERITY_RECOMMENDATIONS = {
    "Healthy": [
        "No treatment required now.",
        "Continue weekly crop checks, especially after rainfall.",
        "Keep field edges weed-free to reduce pest shelter.",
    ],
    "Early": [
        "Inspect neighboring plants for egg masses or young larvae.",
        "Use neem-based biopesticide or approved early-stage treatment.",
        "Re-scan affected plants in 3 to 5 days.",
    ],
    "Moderate": [
        "Apply recommended pesticide at dawn or dusk when larvae are active.",
        "Target leaf whorls and damaged areas during spraying.",
        "Notify nearby farmers and monitor spread across the farm.",
    ],
    "Severe": [
        "Apply Emamectin benzoate 1.9% EC at the approved label rate immediately.",
        "Use Chlorpyrifos 48% EC only where locally approved and with protective gear.",
        "Contact a MoFA extension officer for field confirmation.",
        "Re-scan in 5 to 7 days to track treatment effectiveness.",
    ],
}

SEVERITY_RECOMMENDATIONS_TWI = {
    "Healthy": [
        "Yare biara nni nhaban no so seesei.",
        "Kɔ so hwɛ afuo no dapɛn biara, titiriw sɛ osu tɔ wie a.",
        "Yi nwura fi afuo no ano na mmoawa annya baabi ankɔhyɛ.",
    ],
    "Early": [
        "Hwɛ nnua a ɛbɛn ho sɛ mmoawa nkesua anaa mmoawa nketewa wɔ so.",
        "Fa neem aduru anaa aduru a wɔagye atom ma mfitiaseɛ yare no.",
        "San scan nnua no wɔ nna 3 kosi 5 mu.",
    ],
    "Moderate": [
        "Fa aduru a wɔkamfo kyerɛ no gu so anɔpa anaa anwummere.",
        "Fa aduru no kɔ nhaban mfinimfini ne mmeae a asɛe no so.",
        "Ka kyerɛ akuafo a wɔbɛn wo na hwɛ sɛ ɛretrɛw wɔ afuo no mu anaa.",
    ],
    "Severe": [
        "Fa Emamectin benzoate 1.9% EC sɛnea akwankyerɛ no kyerɛ ntɛm ara.",
        "Fa ahobammɔ nneɛma hyɛ wo ho ansa na wode aduru biara bedi dwuma.",
        "Frɛ MoFA extension officer ma ɔmmɛhwɛ afuo no.",
        "San scan wɔ nna 5 kosi 7 mu de hwɛ sɛ ayaresa no reyɛ adwuma anaa.",
    ],
}

RESULT_TEXT = {
    "English": {
        "title": "AI Detection Results",
        "caption": "Scan completed - demo inference",
        "severe_alert": "<strong>Severe Infestation Detected.</strong> Immediate action required. Contact a MoFA extension officer.",
        "image_caption": "Analyzed image",
        "metadata": "Scan Metadata",
        "location": "Location",
        "crop_stage": "Crop Stage",
        "farm_size": "Farm Size",
        "logged_by": "Logged By",
        "prediction": "Prediction",
        "confidence": "Confidence",
        "recommended_action": "Recommended Action",
        "scan_another": "Scan Another Image",
        "download": "Download Report",
    },
    "Twi": {
        "title": "AI Nhwehwɛmu Aba",
        "caption": "Scan no awie - demo nhwehwɛmu",
        "severe_alert": "<strong>Yare no mu yɛ den.</strong> Ɛsɛ sɛ woyɛ biribi ntɛm. Frɛ MoFA extension officer.",
        "image_caption": "Mfonini a wɔahwɛ mu",
        "metadata": "Scan Ho Nsɛm",
        "location": "Beae",
        "crop_stage": "Afifideɛ Gyinabea",
        "farm_size": "Afuo Kɛseɛ",
        "logged_by": "Nea ɔde hyɛɛ mu",
        "prediction": "Nea AI no hunui",
        "confidence": "Ahotosoɔ",
        "recommended_action": "Nea ɛsɛ sɛ woyɛ",
        "scan_another": "Scan Mfonini Foforɔ",
        "download": "Twe Report",
    },
}

RECENT_SCANS = [
    {"farmer": "Kofi Mensah", "region": "Ashanti", "time": "2 min ago", "severity": "Severe"},
    {"farmer": "Ama Asante", "region": "Brong-Ahafo", "time": "8 min ago", "severity": "Moderate"},
    {"farmer": "Kwame Boateng", "region": "Northern", "time": "15 min ago", "severity": "Healthy"},
]

DISTRICT_REPORTS = [
    {
        "District": "Ejura-Sekyedumase",
        "Region": "Ashanti",
        "Total Scans": 824,
        "Severe": 142,
        "Moderate": 89,
        "Status": "Critical",
    },
    {
        "District": "Sunyani Municipal",
        "Region": "Brong-Ahafo",
        "Total Scans": 712,
        "Severe": 98,
        "Moderate": 134,
        "Status": "Critical",
    },
    {
        "District": "Techiman North",
        "Region": "Brong-Ahafo",
        "Total Scans": 580,
        "Severe": 54,
        "Moderate": 161,
        "Status": "Warning",
    },
    {
        "District": "Nkoranza North",
        "Region": "Brong-Ahafo",
        "Total Scans": 443,
        "Severe": 41,
        "Moderate": 98,
        "Status": "Warning",
    },
    {
        "District": "Tamale Metro",
        "Region": "Northern",
        "Total Scans": 394,
        "Severe": 22,
        "Moderate": 57,
        "Status": "Watch",
    },
    {
        "District": "Kumasi Metro",
        "Region": "Ashanti",
        "Total Scans": 1240,
        "Severe": 8,
        "Moderate": 42,
        "Status": "Normal",
    },
]

HISTORY_DATA = [
    {"date": "Jun 12, 2025 - 2:34 PM", "location": "Ejura, Ashanti", "severity": "Severe", "confidence": 86, "farm": "Farm A - Block 3"},
    {"date": "Jun 10, 2025 - 9:12 AM", "location": "Ejura, Ashanti", "severity": "Moderate", "confidence": 79, "farm": "Farm A - Block 1"},
    {"date": "Jun 7, 2025 - 4:20 PM", "location": "Ejura, Ashanti", "severity": "Healthy", "confidence": 93, "farm": "Farm B - Maize Field"},
    {"date": "Jun 5, 2025 - 11:08 AM", "location": "Ejura, Ashanti", "severity": "Early", "confidence": 72, "farm": "Farm A - Block 2"},
    {"date": "Jun 2, 2025 - 8:45 AM", "location": "Ejura, Ashanti", "severity": "Moderate", "confidence": 81, "farm": "Farm C - Section 2"},
    {"date": "May 30, 2025 - 3:15 PM", "location": "Ejura, Ashanti", "severity": "Severe", "confidence": 91, "farm": "Farm A - Block 4"},
    {"date": "May 28, 2025 - 10:22 AM", "location": "Ejura, Ashanti", "severity": "Early", "confidence": 68, "farm": "Farm B - Section 1"},
    {"date": "May 25, 2025 - 7:50 AM", "location": "Ejura, Ashanti", "severity": "Healthy", "confidence": 97, "farm": "Farm D - New Field"},
]

TREND_DATA = {
    "Date": ["May 14", "May 17", "May 20", "May 23", "May 26", "May 29", "Jun 1", "Jun 4", "Jun 7", "Jun 10", "Jun 12"],
    "Severe": [18, 22, 28, 35, 42, 38, 55, 61, 72, 80, 88],
    "Moderate": [45, 52, 60, 55, 62, 70, 68, 75, 72, 68, 74],
    "Healthy": [140, 135, 128, 120, 112, 108, 102, 96, 88, 84, 78],
}

REGIONAL_ACTIVITY = {
    "Region": ["Ashanti", "B-Ahafo", "Northern", "V/R", "Western", "G/A", "Eastern", "UE/W"],
    "Severe": [142, 98, 22, 18, 12, 8, 35, 44],
    "Moderate": [89, 134, 57, 44, 38, 21, 62, 55],
    "Early": [120, 180, 92, 68, 72, 45, 88, 70],
}
