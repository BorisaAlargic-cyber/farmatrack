"""FarmaTrack — Streamlit dashboard entry point."""

import sys
from pathlib import Path

# Ensure the project root (farmatrack/) is on sys.path so that
# `from dashboard.pages...`, `from config...`, etc. resolve correctly
# regardless of the working directory.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="FarmaTrack",
    page_icon="🐷",
    layout="wide",
)

# ── Sidebar navigation ────────────────────────────────────
PAGES = {
    "📊 Dashboard": "dashboard",
    "📷 Scan": "scan",
    "🐖 Herd": "herd",
    "🏠 Pens": "pens",
    "💊 Health": "health",
    "🍼 Farrowings": "farrowings",
}

st.sidebar.title("🐷 FarmaTrack")
st.sidebar.markdown("---")
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
