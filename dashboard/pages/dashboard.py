"""Dashboard overview page — KPIs, charts, pen utilisation."""

import streamlit as st
import pandas as pd
from dashboard import api_client as api


def render():
    st.title("📊 Dashboard")

    try:
        data = api.get_summary()
    except Exception as e:
        st.error(f"Could not load dashboard: {e}")
        return

    # ── KPI row ────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Active Pigs", data["total_active_pigs"])
    k2.metric("Sick / Quarantined", data["sick_or_quarantined"])
    k3.metric("Total Farrowings", data["total_farrowings"])
    k4.metric("Avg Live Born", data["avg_live_born"])

    st.markdown("---")

    # ── Herd by category ───────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Herd by Category")
        cat = data.get("by_category", {})
        if cat:
            df_cat = pd.DataFrame({"category": cat.keys(), "count": cat.values()})
            st.bar_chart(df_cat.set_index("category"))
        else:
            st.info("No pig data yet.")

    with col2:
        st.subheader("Health Distribution")
        hd = data.get("health_distribution", {})
        if hd:
            df_hd = pd.DataFrame({"status": hd.keys(), "count": hd.values()})
            st.bar_chart(df_hd.set_index("status"))
        else:
            st.info("No health records yet.")

    # ── Pen utilisation ────────────────────────────────────
    st.markdown("---")
    st.subheader("Pen Utilisation")
    pens = data.get("pen_utilisation", [])
    if pens:
        df_pen = pd.DataFrame(pens)
        st.dataframe(
            df_pen[["name", "capacity", "current", "utilisation_pct"]].rename(
                columns={"name": "Pen", "capacity": "Capacity", "current": "Current", "utilisation_pct": "Util %"}
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No pens found.")
