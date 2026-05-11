"""Farrowings page — list, add, update farrowing records."""

import streamlit as st
import pandas as pd
from datetime import date
from dashboard import api_client as api


def render():
    st.title("🍼 Farrowings")

    tab_list, tab_add = st.tabs(["Records", "New Farrowing"])

    with tab_list:
        sow_filter = st.number_input("Filter by Sow ID (0 = all)", min_value=0, value=0, step=1)
        try:
            rows = api.list_farrowings(sow_id=sow_filter if sow_filter else None)
        except Exception as e:
            st.error(str(e))
            return

        if rows:
            df = pd.DataFrame(rows)
            df["total_born"] = df["live_born"] + df["stillborn"] + df["mummified"]
            st.dataframe(
                df[["id", "sow_id", "farrowing_date", "live_born", "stillborn", "mummified", "total_born", "weaned_count", "wean_date"]],
                use_container_width=True,
                hide_index=True,
            )

            with st.expander("Update weaning data"):
                far_id = st.number_input("Farrowing ID", min_value=1, step=1, key="edit_far")
                weaned = st.number_input("Weaned Count", min_value=0, step=1, key="edit_weaned")
                wean_dt = st.date_input("Wean Date", value=date.today(), key="edit_wdt")
                if st.button("💾 Update"):
                    try:
                        api.update_farrowing(far_id, {"weaned_count": weaned, "wean_date": str(wean_dt)})
                        st.success("Updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("No farrowing records found.")

    with tab_add:
        with st.form("add_farrowing"):
            sow_id = st.number_input("Sow ID *", min_value=1, step=1)
            far_date = st.date_input("Farrowing Date *", value=date.today())
            live = st.number_input("Live Born *", min_value=0, value=10, step=1)
            still = st.number_input("Stillborn", min_value=0, value=0, step=1)
            mumm = st.number_input("Mummified", min_value=0, value=0, step=1)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("➕ Add Farrowing")

        if submitted:
            payload = {
                "sow_id": sow_id,
                "farrowing_date": str(far_date),
                "live_born": live,
                "stillborn": still,
                "mummified": mumm,
                "notes": notes or None,
            }
            try:
                api.create_farrowing(payload)
                st.success("Farrowing recorded!")
            except Exception as e:
                st.error(str(e))
