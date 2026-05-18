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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
/* ── Hide auto Streamlit nav ── */
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar background ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #2C2A1E !important;
}

/* ── Nav links ── */
.nav-link {
    display: flex;
    align-items: center;
    gap: 9px;
    text-decoration: none !important;
    color: rgba(245,240,232,0.55) !important;
    font-size: 0.82rem;
    font-weight: 400;
    padding: 8px 14px 8px 16px;
    border-radius: 6px;
    margin: 1px 0;
    line-height: 1.3;
    border-left: 2px solid transparent;
    transition: color 0.15s, background 0.15s;
}
.nav-link:hover {
    background: rgba(255,255,255,0.05);
    color: rgba(245,240,232,0.9) !important;
    text-decoration: none !important;
}
.nav-link-active {
    display: flex;
    align-items: center;
    gap: 9px;
    text-decoration: none !important;
    color: #c8d49a !important;
    font-size: 0.82rem;
    font-weight: 400;
    padding: 8px 14px 8px 14px;
    border-radius: 6px;
    margin: 1px 0;
    line-height: 1.3;
    background: rgba(154,171,94,0.12);
    border-left: 2px solid #9aab5e;
}

/* ── Nav icon size ── */
.nav-link i, .nav-link-active i { font-size: 15px; flex-shrink: 0; }

/* ── Section headers ── */
.nav-section {
    color: #6B6450;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    padding: 16px 0 5px 16px;
}

/* ── Sidebar footer (user avatar) ── */
.sidebar-footer {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin-top: 8px;
}
.user-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: #6B8540;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; color: #F5F0E8;
    flex-shrink: 0;
}
.user-name { font-size: 12px; color: rgba(245,240,232,0.8); font-weight: 500; }
.user-role { font-size: 10px; color: #6B6450; }

/* ── Sidebar hr ── */
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
page_key = st.query_params.get("page", "dashboard")

def _link(label, key, icon="ti-circle"):
    cls = "nav-link-active" if page_key == key else "nav-link"
    return f'<a href="?page={key}" class="{cls}" target="_self"><i class="ti {icon}"></i>{label}</a>'

st.sidebar.markdown("""
<div style='padding:8px 0 4px 0;'>
    <div style='font-size:1.4rem;font-weight:700;color:#F5F0E8;'>FarmaTrack</div>
    <div style='font-size:0.68rem;color:#6B6450;letter-spacing:0.12em;text-transform:uppercase;margin-top:2px;'>Farm Management</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown(f"""
<div class='nav-section'>OVERVIEW</div>
{_link("Dashboard", "dashboard", "ti-layout-dashboard")}
<div class='nav-section'>ANIMALS</div>
{_link("Pig Registry", "herd", "ti-ear")}
{_link("Pens &amp; Enclosures", "pens", "ti-home-2")}
{_link("Farrowing", "farrowings", "ti-clipboard-list")}
<div class='nav-section'>OPERATIONS</div>
{_link("Health", "health", "ti-heart-plus")}
{_link("OCR Scan", "scan", "ti-scan")}
<div style="margin-top:24px; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; display:flex; align-items:center; gap:10px; padding-left:14px;">
    <div class="user-avatar">BK</div>
    <div>
        <div class="user-name">Boriša K.</div>
        <div class="user-role">Administrator</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Page render ────────────────────────────────────────────
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
else:
    from dashboard.pages.dashboard import render

render()
