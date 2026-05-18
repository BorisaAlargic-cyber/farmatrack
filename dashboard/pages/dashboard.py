"""Dashboard overview page — KPIs, upcoming farrowings, health distribution, pen utilisation."""

import streamlit as st
import pandas as pd
from dashboard import api_client as api


_FILTERS = {
    "Today": 0,
    "Tomorrow": 1,
    "Next 7 Days": 7,
    "Next Month": 30,
    "Next 3 Months": 90,
}


def _status_label(days_left: int) -> str:
    if days_left < 0:
        return f"⚠️ Overdue {abs(days_left)}d"
    if days_left == 0:
        return "🔴 Today!"
    if days_left == 1:
        return "🟠 Tomorrow"
    if days_left <= 7:
        return f"🟡 In {days_left} days"
    return f"🟢 In {days_left} days"


def render():
    st.title("📊 Dashboard")

    try:
        data = api.get_summary()
    except Exception as e:
        st.error(f"Could not load dashboard: {e}")
        return

    # ── KPI row ────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active Pigs", data["total_active_pigs"])
    k2.metric("Sick / Quarantined", data["sick_or_quarantined"])
    k3.metric("Total Farrowings", data["total_farrowings"])
    k4.metric("Avg Live Born", data["avg_live_born"])

    st.markdown("---")

    # ── Upcoming farrowings ────────────────────────────────
    st.subheader("🐷 Upcoming Farrowings")

    selected = st.radio(
        "Show farrowings for:",
        list(_FILTERS.keys()),
        index=2,
        horizontal=True,
        label_visibility="collapsed",
    )

    days = _FILTERS[selected]

    try:
        upcoming = api.list_upcoming_farrowings(days_ahead=days)
    except Exception as e:
        st.error(str(e))
        upcoming = []

    if upcoming:
        rows = []
        for u in upcoming:
            rows.append({
                "Ear Tag": u["ear_tag"],
                "Pen": u["pen"],
                "Insemination Date": u["insemination_date"],
                "Expected Farrowing": u["expected_farrowing_date"],
                "Status": _status_label(u["days_left"]),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(rows)} sow(s)")
    else:
        st.info(f"No inseminated sows for: **{selected}**.")

    st.markdown("---")

    # ── Health distribution + pen utilisation ──────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Health Distribution")
        hd = data.get("health_distribution", {})
        if hd:
            df_hd = pd.DataFrame({"Status": hd.keys(), "Count": hd.values()})
            st.bar_chart(df_hd.set_index("Status"))
        else:
            st.info("No health records yet.")

    with col2:
        st.subheader("Pen Utilisation")
        pens = data.get("pen_utilisation", [])
        if pens:
            df_pen = pd.DataFrame(pens)
            st.dataframe(
                df_pen[["name", "capacity", "current", "utilisation_pct"]].rename(
                    columns={
                        "name": "Pen",
                        "capacity": "Capacity",
                        "current": "Current",
                        "utilisation_pct": "Util %",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No pens found.")
