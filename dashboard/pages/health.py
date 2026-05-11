"""Health records page — view, add, edit health entries."""

import streamlit as st
import pandas as pd
from datetime import date
from dashboard import api_client as api
from dashboard.components.status_badge import status_badge

STATUSES = ["healthy", "sick", "treated", "quarantined"]


def render():
    st.title("💊 Health Records")

    tab_list, tab_add = st.tabs(["Records", "New Record"])

    with tab_list:
        pig_filter = st.number_input("Filter by Pig ID (0 = all)", min_value=0, value=0, step=1)
        try:
            records = api.list_health_records(pig_id=pig_filter if pig_filter else None)
        except Exception as e:
            st.error(str(e))
            return

        if records:
            df = pd.DataFrame(records)
            st.dataframe(
                df[["id", "pig_id", "status", "diagnosis", "treatment", "vet_name", "record_date", "next_checkup"]],
                use_container_width=True,
                hide_index=True,
            )

            with st.expander("Edit a record"):
                rec_id = st.number_input("Record ID", min_value=1, step=1, key="edit_hr")
                new_status = st.selectbox("Status", STATUSES, key="edit_status")
                new_diag = st.text_input("Diagnosis", key="edit_diag")
                new_treat = st.text_input("Treatment", key="edit_treat")
                new_next = st.date_input("Next checkup", value=None, key="edit_next")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Update"):
                        payload = {"status": new_status}
                        if new_diag:
                            payload["diagnosis"] = new_diag
                        if new_treat:
                            payload["treatment"] = new_treat
                        if new_next:
                            payload["next_checkup"] = str(new_next)
                        try:
                            api.update_health_record(rec_id, payload)
                            st.success("Updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with col2:
                    if st.button("🗑️ Delete"):
                        try:
                            api.delete_health_record(rec_id)
                            st.success("Deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        else:
            st.info("No health records found.")

    with tab_add:
        with st.form("add_health"):
            pig_id = st.number_input("Pig ID *", min_value=1, step=1)
            status = st.selectbox("Status *", STATUSES)
            diagnosis = st.text_input("Diagnosis")
            treatment = st.text_area("Treatment")
            vet = st.text_input("Vet Name")
            rec_date = st.date_input("Record Date", value=date.today())
            next_chk = st.date_input("Next Checkup", value=None)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("➕ Add Record")

        if submitted:
            payload = {
                "pig_id": pig_id,
                "status": status,
                "diagnosis": diagnosis or None,
                "treatment": treatment or None,
                "vet_name": vet or None,
                "record_date": str(rec_date),
                "next_checkup": str(next_chk) if next_chk else None,
                "notes": notes or None,
            }
            try:
                api.create_health_record(payload)
                st.success("Health record added!")
            except Exception as e:
                st.error(str(e))
