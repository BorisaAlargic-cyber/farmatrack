"""Colour-coded health status badge."""

import streamlit as st

_COLORS = {
    "healthy": "🟢",
    "sick": "🔴",
    "treated": "🟡",
    "quarantined": "🟠",
}


def status_badge(status: str):
    icon = _COLORS.get(status, "⚪")
    st.markdown(f"{icon} **{status.capitalize()}**")
