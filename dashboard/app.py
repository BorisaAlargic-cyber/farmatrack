"""FarmaTrack — Streamlit dashboard entry point."""

import sys
import os
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

_db_url = None
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ[_k] = _v
    _db_url = st.secrets.get("DATABASE_URL")
except Exception:
    pass

from database.connection import init_db
init_db(database_url=_db_url)

st.set_page_config(
    page_title="FarmaTrack",
    page_icon="🐷",
    layout="wide",
)

st.markdown("""
<style>
/* ── Hide auto Streamlit nav ── */
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar background ── */
section[data-testid="stSidebar"] {
    background-color: #2C2A1E !important;
}
section[data-testid="stSidebar"] > div {
    background-color: #2C2A1E !important;
}

/* ── All sidebar text ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #D4CDB8 !important;
}

/* ── Sidebar title ── */
section[data-testid="stSidebar"] h1 {
    color: #F5F0E8 !important;
    font-size: 1.6rem !important;
    letter-spacing: 0.02em;
}

/* ── Section headers (OVERVIEW / ANIMALS / OPERATIONS) ── */
section[data-testid="stSidebar"] .section-header {
    color: #7A7260 !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 16px 0 4px 0;
}

/* ── Radio nav items ── */
section[data-testid="stSidebar"] .stRadio label {
    color: #D4CDB8 !important;
    font-size: 0.95rem;
    padding: 4px 8px;
    border-radius: 6px;
    cursor: pointer;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #F5F0E8 !important;
    background-color: rgba(255,255,255,0.08);
}

/* ── Sidebar divider ── */
section[data-testid="stSidebar"] hr {
    border-color: #3E3C2E !important;
    margin: 6px 0;
}

/* ── Main background ── */
.stApp { background-color: #F7F3EC; }
.main .block-container { background-color: #F7F3EC; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 16px !important;
    border: 1px solid #E0D9CC;
    box-shadow: 0 1px 3px rgba(44,42,30,0.06);
}
[data-testid="stMetricValue"] { color: #2C2A1E !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #7A7260 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Dataframes / tables ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E0D9CC;
}

/* ── Containers with border ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border-radius: 12px !important;
    border-color: #E0D9CC !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
}
.stButton > button[kind="primary"] {
    background-color: #6B8540 !important;
    border-color: #6B8540 !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #5A7234 !important;
    border-color: #5A7234 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #EDE8DE;
    border-radius: 8px;
    padding: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #5A5444;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #2C2A1E !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────
st.sidebar.markdown("# 🐷 FarmaTrack")
st.sidebar.markdown("<p style='color:#7A7260;font-size:0.75rem;margin-top:-12px;letter-spacing:0.08em;'>FARM MANAGEMENT</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("<p class='section-header'>OVERVIEW</p>", unsafe_allow_html=True)
PAGES = {
    "⬛ Dashboard":   "dashboard",
    "📷 Scan Tag":    "scan",
    "🐖 Pig Registry": "herd",
    "🏠 Pens":        "pens",
    "💊 Health":      "health",
    "🍼 Farrowings":  "farrowings",
}

selection = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
page_key = PAGES[selection]

# ── Dynamic page import ───────────────────────────────────
if page_key == "dashboard":
    from dashboard.pages.dashboard import render
elif page_key == "scan":
    from dashboard.pages.scan import render
elif page_key == "herd":
    from dashboard.pages.herd import render
elif page_key == "pens":
    from dashboard.pages.pens import render
elif page_key == "health":
    from dashboard.pages.health import render
elif page_key == "farrowings":
    from dashboard.pages.farrowings import render

render()
