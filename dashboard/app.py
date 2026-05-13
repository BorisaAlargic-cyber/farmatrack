"""FarmaTrack — Streamlit dashboard entry point."""

import sys
import os
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# Inject all string secrets into os.environ so pydantic-settings picks them up
# (e.g. GOOGLE_VISION_API_KEY, TESSERACT_CMD).
# DATABASE_URL is also passed directly to init_db() to bypass any stale env value.
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

# Hide the auto-generated Streamlit pages nav (we use our own radio nav)
st.markdown(
    "<style>[data-testid='stSidebarNav'] { display: none; }</style>",
    unsafe_allow_html=True,
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
