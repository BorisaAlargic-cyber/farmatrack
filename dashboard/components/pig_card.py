"""Reusable pig detail card for Streamlit."""

import streamlit as st
from dashboard.components.status_badge import status_badge


def pig_card(pig: dict, compact: bool = False):
    """Render a pig info card. If compact, show a single-line summary."""
    if compact:
        active = "✅" if pig.get("is_active") else "❌"
        st.markdown(
            f"**{pig['ear_tag']}** | {pig['category']} | "
            f"{pig.get('breed', '—')} | {pig.get('weight_kg', '?')} kg | {active}"
        )
        return

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.markdown(f"### 🏷️ {pig['ear_tag']}")
            st.caption(f"ID: {pig['id']}")
        with c2:
            st.markdown(f"**Category:** {pig['category']}")
            st.markdown(f"**Breed:** {pig.get('breed') or '—'}")
            st.markdown(f"**Weight:** {pig.get('weight_kg') or '?'} kg")
        with c3:
            if pig.get("is_active"):
                st.success("Active")
            else:
                st.error("Inactive")
        if pig.get("notes"):
            st.info(pig["notes"])
