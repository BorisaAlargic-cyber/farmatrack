"""Dashboard overview page — KPIs, predstojeća prasenja, distribucija zdravlja, iskorišćenost tora."""

import streamlit as st
import pandas as pd
from dashboard import api_client as api


_FILTERS = {
    "Danas": 0,
    "Sutra": 1,
    "Narednih 7 dana": 7,
    "Mesec dana": 30,
    "3 meseca": 90,
}


def _status_label(days_left: int) -> str:
    if days_left < 0:
        return f"⚠️ Kasni {abs(days_left)} d."
    if days_left == 0:
        return "🔴 Danas!"
    if days_left == 1:
        return "🟠 Sutra"
    if days_left <= 7:
        return f"🟡 Za {days_left} dana"
    return f"🟢 Za {days_left} dana"


def render():
    st.title("📊 Dashboard")

    try:
        data = api.get_summary()
    except Exception as e:
        st.error(f"Greška pri učitavanju: {e}")
        return

    # ── KPI red ────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Aktivnih svinja", data["total_active_pigs"])
    k2.metric("Bolesnih / Karantin", data["sick_or_quarantined"])
    k3.metric("Ukupno prasenja", data["total_farrowings"])
    k4.metric("Prosečno živih prasadi", data["avg_live_born"])

    st.markdown("---")

    # ── Predstojeća prasenja ───────────────────────────────
    st.subheader("🐷 Predstojeća prasenja")

    selected = st.radio(
        "Prikaži prasenja za:",
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
                "Markica": u["ear_tag"],
                "Tor": u["pen"],
                "Osemenjeno": u["insemination_date"],
                "Očekivano prasenje": u["expected_farrowing_date"],
                "Status": _status_label(u["days_left"]),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Prikazano: {len(rows)} krmača")
    else:
        st.info(f"Nema osemenjenih krmača za period: **{selected}**.")

    st.markdown("---")

    # ── Distribucija zdravlja + iskorišćenost tora ─────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribucija zdravlja")
        hd = data.get("health_distribution", {})
        if hd:
            df_hd = pd.DataFrame({"Status": hd.keys(), "Broj": hd.values()})
            st.bar_chart(df_hd.set_index("Status"))
        else:
            st.info("Nema zdravstvenih zapisa.")

    with col2:
        st.subheader("Iskorišćenost torova")
        pens = data.get("pen_utilisation", [])
        if pens:
            df_pen = pd.DataFrame(pens)
            st.dataframe(
                df_pen[["name", "capacity", "current", "utilisation_pct"]].rename(
                    columns={
                        "name": "Tor",
                        "capacity": "Kapacitet",
                        "current": "Trenutno",
                        "utilisation_pct": "Popunjenost %",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nema torova.")
