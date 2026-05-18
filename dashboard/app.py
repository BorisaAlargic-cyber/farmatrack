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
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #2C2A1E !important;
}

/* ── Sidebar buttons — flat nav items ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #F5F0E8 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 6px 12px 6px 16px !important;
    border-radius: 7px !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    width: 100% !important;
    box-shadow: none !important;
    margin: 1px 0 !important;
    transition: background 0.15s;
    display: flex !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.09) !important;
    color: #F5F0E8 !important;
}
section[data-testid="stSidebar"] .stButton > button:focus,
section[data-testid="stSidebar"] .stButton > button:active {
    box-shadow: none !important;
    outline: none !important;
    color: #F5F0E8 !important;
}

/* ── Active nav item (injected as markdown) ── */
.nav-active {
    background-color: #3E3B2A;
    color: #F5F0E8;
    padding: 6px 12px 6px 13px;
    border-radius: 7px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 1px 0;
    cursor: default;
    border-left: 3px solid #6B8540;
}

/* ── Section headers ── */
.nav-section {
    color: #6B6450 !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    padding: 18px 4px 5px 16px;
    margin: 0;
}

/* ── Sidebar title area ── */
section[data-testid="stSidebar"] h1 {
    color: #F5F0E8 !important;
    font-size: 1.5rem !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] p {
    color: #7A7260 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #3E3C2E !important;
    margin: 8px 0 4px 0;
}

/* ── Main background ── */
.stApp, .main .block-container { background-color: #F7F3EC; }

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

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E0D9CC;
}

/* ── Containers with border ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border-color: #E0D9CC !important;
}

/* ── Primary buttons ── */
.stButton > button[kind="primary"] {
    background-color: #6B8540 !important;
    border-color: #6B8540 !important;
    color: white !important;
    border-radius: 8px;
}
.stButton > button[kind="primary"]:hover {
    background-color: #5A7234 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #EDE8DE;
    border-radius: 8px;
    padding: 2px;
}
.stTabs [data-baseweb="tab"] { border-radius: 6px; color: #5A5444; }
.stTabs [aria-selected="true"] { background-color: #FFFFFF !important; color: #2C2A1E !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
if "_page" not in st.session_state:
    st.session_state["_page"] = "dashboard"

def _nav(label, key):
    if st.session_state["_page"] == key:
        st.sidebar.markdown(f"<div class='nav-active'>{label}</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state["_page"] = key
            st.rerun()

st.sidebar.markdown("""
<div style='padding: 8px 0 4px 0;'>
    <div style='font-size:1.4rem;font-weight:700;color:#F5F0E8;letter-spacing:0.01em;'>FarmaTrack</div>
    <div style='font-size:0.68rem;color:#6B6450;letter-spacing:0.12em;text-transform:uppercase;margin-top:2px;'>Farm Management</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("<div class='nav-section'>OVERVIEW</div>", unsafe_allow_html=True)
_nav("Dashboard",       "dashboard")

st.sidebar.markdown("<div class='nav-section'>ANIMALS</div>", unsafe_allow_html=True)
_nav("Pig Registry",       "herd")
_nav("Pens & Enclosures",  "pens")
_nav("Farrowing",          "farrowings")

st.sidebar.markdown("<div class='nav-section'>OPERATIONS</div>", unsafe_allow_html=True)
_nav("Health",    "health")
_nav("OCR Scan",  "scan")

# ── Page render ────────────────────────────────────────────
page_key = st.session_state["_page"]

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
