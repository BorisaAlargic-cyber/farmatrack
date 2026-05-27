"""Reusable pig detail card for Streamlit."""

from datetime import date
from dashboard import api_client as api

import streamlit as st


# ── Predefined vaccines / medications ─────────────────────────────────────────
VACCINES_AND_MEDS = [
    "PRRS Vaccine",
    "Mycoplasma (Enzootic Pneumonia) Vaccine",
    "PCV2 (Circovirus) Vaccine",
    "Erysipelas Vaccine",
    "Parvovirus Vaccine",
    "FMD (Foot-and-Mouth) Vaccine",
    "Rotavirus Vaccine",
    "E. coli Vaccine",
    "Ivermectin (Dewormer)",
    "Fenbendazole (Dewormer)",
    "Amoxicillin",
    "Enrofloxacin",
    "Oxytetracycline",
    "Ceftiofur",
    "Penicillin",
    "Iron Injection",
    "Vitamin B Complex",
    "Vitamin E / Selenium",
    "Oxytocin",
    "Other",
]

_STATUS_OPTIONS = ["healthy", "sick", "treated", "quarantined"]
_STATUS_LABELS  = {
    "healthy":     "✅ Healthy",
    "sick":        "🤒 Sick",
    "treated":     "💊 Treated",
    "quarantined": "🔒 Quarantined",
}


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


# ── Dialogs ────────────────────────────────────────────────────────────────────

@st.dialog("➕ Add Health Record")
def _health_dialog(pig_id: int, ear_tag: str):
    st.markdown(f"Pig: **{ear_tag}**")
    st.divider()

    record_date = st.date_input("Date", value=date.today(), max_value=date.today())

    status = st.selectbox(
        "Status *",
        _STATUS_OPTIONS,
        format_func=lambda x: _STATUS_LABELS[x],
    )

    treatment_sel = st.selectbox("Vaccine / Medication", ["— None —"] + VACCINES_AND_MEDS)
    treatment = None
    if treatment_sel == "Other":
        treatment = st.text_input("Specify vaccine / medication")
    elif treatment_sel != "— None —":
        treatment = treatment_sel

    diagnosis = st.text_input("Diagnosis / Notes (optional)")
    vet_name  = st.text_input("Vet name (optional)")

    col1, col2 = st.columns(2)
    with col1:
        next_checkup = st.date_input("Next checkup (optional)", value=None)

    st.divider()
    if st.button("✅ Save", type="primary", use_container_width=True):
        try:
            api.create_health_record({
                "pig_id":       pig_id,
                "status":       status,
                "diagnosis":    diagnosis or None,
                "treatment":    treatment,
                "vet_name":     vet_name or None,
                "record_date":  record_date,
                "next_checkup": next_checkup,
            })
            st.success("Health record saved!")
            st.rerun()
        except Exception as e:
            st.error(str(e))


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
        live_born  = st.number_input("🟢 Live Born",   min_value=0, value=0, step=1)
    with col2:
        stillborn  = st.number_input("💀 Stillborn",   min_value=0, value=0, step=1)
    with col3:
        mummified  = st.number_input("🔴 Mummified",   min_value=0, value=0, step=1)

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


# ── Health section ─────────────────────────────────────────────────────────────

def _health_section(pig: dict):
    pig_id   = pig["id"]
    ear_tag  = pig["ear_tag"]

    try:
        records = api.list_health_records(pig_id=pig_id)
    except Exception:
        records = []

    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown(f"#### 🏥 Health Records &nbsp;&nbsp; `{len(records)} record(s)`")
    with col_btn:
        if st.button("➕ Add Record", key=f"health_btn_{pig_id}", use_container_width=True, type="primary"):
            _health_dialog(pig_id, ear_tag)

    if not records:
        st.caption("No health records yet.")
        return

    for r in records:
        status = r.get("status", "healthy")
        status_label = _STATUS_LABELS.get(status, status.title())
        record_date  = _fmt(r.get("record_date"))
        treatment    = r.get("treatment") or "—"
        diagnosis    = r.get("diagnosis") or ""
        vet          = r.get("vet_name") or ""
        next_chk     = r.get("next_checkup")

        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{record_date}** — {status_label}")
            with c2:
                if status == "sick":
                    st.error(status_label, icon="🤒")
                elif status == "quarantined":
                    st.error(status_label, icon="🔒")
                elif status == "treated":
                    st.warning(status_label, icon="💊")
                else:
                    st.success(status_label, icon="✅")

            info_col, treat_col = st.columns(2)
            with info_col:
                if diagnosis:
                    st.caption("Diagnosis")
                    st.write(diagnosis)
                if vet:
                    st.caption("Vet")
                    st.write(vet)
            with treat_col:
                if treatment != "—":
                    st.caption("Vaccine / Medication")
                    st.write(treatment)
                if next_chk:
                    st.caption("Next checkup")
                    st.write(_fmt(next_chk))


# ── Reproductive section ───────────────────────────────────────────────────────

def _reproductive_section(pig: dict):
    sow_id  = pig["id"]
    ear_tag = pig["ear_tag"]

    try:
        farrowings = api.list_farrowings(sow_id=sow_id)
    except Exception:
        farrowings = []

    completed = [f for f in farrowings if f.get("farrowing_date")]

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
        num       = f.get("farrowing_number", "?")
        ins_date  = _parse_date(f.get("insemination_date"))
        exp_date  = _parse_date(f.get("expected_farrowing_date"))
        farr_date = _parse_date(f.get("farrowing_date"))
        live      = f.get("live_born")
        stillborn = f.get("stillborn", 0)
        mumif     = f.get("mummified", 0)
        total     = f.get("total_born", 0)

        with st.container(border=True):
            if farr_date:
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


# ── Main pig card ──────────────────────────────────────────────────────────────

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

        is_sow = pig.get("category") in ("sow", "gilt")

        if is_sow:
            tab_health, tab_repro = st.tabs(["🏥 Health Records", "📅 Reproductive History"])
            with tab_health:
                _health_section(pig)
            with tab_repro:
                _reproductive_section(pig)
        else:
            st.divider()
            _health_section(pig)
