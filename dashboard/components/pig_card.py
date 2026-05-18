"""Reusable pig detail card for Streamlit."""

from datetime import date
from dashboard import api_client as api

import streamlit as st


def _fmt(d) -> str:
    if d is None:
        return "—"
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except ValueError:
            return d
    return d.strftime("%d.%m.%Y")


def _parse_date(d):
    if d is None:
        return None
    if isinstance(d, str):
        return date.fromisoformat(d)
    return d


# ── Dialogs ────────────────────────────────────────────────────────────────

@st.dialog("➕ Add Insemination")
def _insemination_dialog(sow_id: int, ear_tag: str):
    st.markdown(f"Sow: **{ear_tag}**")
    from datetime import timedelta
    insemination_date = st.date_input("Insemination Date", value=date.today(), max_value=date.today())
    expected = insemination_date + timedelta(days=114)
    days_left = (expected - date.today()).days
    st.info(f"Expected farrowing: **{_fmt(expected)}** — in {days_left} days")

    if st.button("✅ Save", type="primary", use_container_width=True):
        try:
            api.add_insemination(sow_id, insemination_date)
            st.success("Insemination recorded!")
            st.rerun()
        except Exception as e:
            st.error(str(e))


@st.dialog("🐷 Record Farrowing")
def _farrowing_dialog(farrowing_id: int, ear_tag: str, expected_date, farrowing_number: int):
    st.markdown(f"Sow: **{ear_tag}** — Farrowing **#{farrowing_number}**")
    if expected_date:
        st.caption(f"Expected: {_fmt(expected_date)}")
    st.divider()

    farrowing_date = st.date_input("Farrowing Date", value=date.today(), max_value=date.today())
    col1, col2, col3 = st.columns(3)
    with col1:
        live_born = st.number_input("🟢 Live Born", min_value=0, value=0, step=1)
    with col2:
        stillborn = st.number_input("💀 Stillborn", min_value=0, value=0, step=1)
    with col3:
        mummified = st.number_input("🔴 Mummified", min_value=0, value=0, step=1)

    total = live_born + stillborn + mummified
    if total > 0:
        st.metric("Total Born", total)

    st.divider()
    if st.button("✅ Save Farrowing", type="primary", use_container_width=True):
        try:
            api.record_farrowing(farrowing_id, farrowing_date, live_born, stillborn, mummified)
            st.success(f"Farrowing recorded! Live: {live_born} | Stillborn: {stillborn} | Mummified: {mummified}")
            st.rerun()
        except Exception as e:
            st.error(str(e))


# ── Reproductive history section ───────────────────────────────────────────

def _reproductive_section(pig: dict):
    sow_id = pig["id"]
    ear_tag = pig["ear_tag"]

    try:
        farrowings = api.list_farrowings(sow_id=sow_id)
    except Exception:
        farrowings = []

    completed = [f for f in farrowings if f.get("farrowing_date")]

    st.divider()
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown(f"#### 📅 Reproductive History &nbsp;&nbsp; `{len(completed)} farrowing(s)`")
    with col_btn:
        if st.button("➕ Insemination", key=f"ins_btn_{sow_id}", use_container_width=True, type="primary"):
            _insemination_dialog(sow_id, ear_tag)

    if not farrowings:
        st.caption("No reproductive history recorded yet.")
        return

    for f in farrowings:
        num = f.get("farrowing_number", "?")
        ins_date = _parse_date(f.get("insemination_date"))
        exp_date = _parse_date(f.get("expected_farrowing_date"))
        farr_date = _parse_date(f.get("farrowing_date"))
        live = f.get("live_born")
        stillborn = f.get("stillborn", 0)
        mumif = f.get("mummified", 0)
        total = f.get("total_born", 0)

        with st.container(border=True):
            if farr_date:
                header_col, _ = st.columns([4, 1])
                with header_col:
                    st.markdown(f"**Farrowing #{num}** — ✅ Completed")

                info_col, live_col, dead_col, mum_col = st.columns(4)
                with info_col:
                    if ins_date:
                        st.caption("📅 Insemination")
                        st.write(_fmt(ins_date))
                    st.caption("🐣 Farrowing Date")
                    st.write(_fmt(farr_date))
                with live_col:
                    st.metric("🟢 Live", live if live is not None else 0)
                with dead_col:
                    st.metric("💀 Stillborn", stillborn)
                with mum_col:
                    st.metric("🔴 Mummified", mumif)

                if total > 0:
                    st.caption(f"Total born: **{total}**")
                if f.get("weaned_count") is not None:
                    st.caption(f"Weaned: **{f['weaned_count']}**")

            else:
                header_col, btn_col = st.columns([3, 1])
                with header_col:
                    st.markdown(f"**Farrowing #{num}** — ⏳ Pending")
                with btn_col:
                    if st.button("📝 Record", key=f"farr_btn_{f['id']}", use_container_width=True):
                        _farrowing_dialog(f["id"], ear_tag, exp_date, num)

                info_col, pred_col = st.columns(2)
                with info_col:
                    st.caption("📅 Insemination Date")
                    st.write(_fmt(ins_date) if ins_date else "—")
                with pred_col:
                    st.caption("🗓️ Expected Farrowing")
                    if exp_date:
                        days_left = (exp_date - date.today()).days
                        if days_left > 0:
                            st.write(f"{_fmt(exp_date)}")
                            st.caption(f"In {days_left} days")
                        elif days_left == 0:
                            st.warning("Expected date is today!")
                        else:
                            st.error(f"Overdue by {abs(days_left)} days (expected: {_fmt(exp_date)})")
                    else:
                        st.write("—")


# ── Main pig card ──────────────────────────────────────────────────────────

def pig_card(pig: dict, compact: bool = False):
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

        if pig.get("category") in ("sow", "gilt"):
            _reproductive_section(pig)
