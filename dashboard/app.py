"""FarmaTrack — Streamlit dashboard entry point."""

import sys
import os
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# Inject Streamlit Cloud secrets into environment variables BEFORE
# any database modules are imported, so pydantic-settings picks them up.
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str) and _k not in os.environ:
            os.environ[_k] = _v
except Exception:
    pass

# Temporary debug — shows masked DATABASE_URL so we can verify the secret is correct
try:
    import re
    _raw = st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL", "NOT SET")
    _masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", _raw)
    st.sidebar.caption(f"🔌 DB: `{_masked}`")
except Exception:
    pass

from config import get_settings
get_settings.cache_clear()

from database.connection import init_db
init_db()

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
