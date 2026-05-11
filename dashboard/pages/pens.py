"""Pens management page — view occupancy, add / edit pens."""

import streamlit as st
import pandas as pd
from dashboard import api_client as api


def render():
    st.title("🏠 Pens")

    tab_list, tab_add = st.tabs(["All Pens", "Add Pen"])

    with tab_list:
        try:
            pens = api.list_pens()
        except Exception as e:
            st.error(str(e))
            return

        if not pens:
            st.info("No pens yet.")
            return

        df = pd.DataFrame(pens)
        df["util_bar"] = df.apply(
            lambda r: f"{r['current_count']}/{r['capacity']} ({round(r['current_count']/r['capacity']*100)}%)" if r["capacity"] else "—",
            axis=1,
        )
        st.dataframe(
            df[["id", "name", "pen_type", "capacity", "current_count", "util_bar"]].rename(
                columns={"name": "Pen", "pen_type": "Type", "capacity": "Cap", "current_count": "Current", "util_bar": "Utilisation"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("Edit a pen"):
            pen_id = st.number_input("Pen ID", min_value=1, step=1, key="edit_pen_id")
            new_name = st.text_input("New name (leave blank to keep)")
            new_cap = st.number_input("New capacity (0 to keep)", min_value=0, step=1)
            if st.button("💾 Update Pen"):
                payload = {}
                if new_name.strip():
                    payload["name"] = new_name.strip()
                if new_cap > 0:
                    payload["capacity"] = new_cap
                if payload:
                    try:
                        api.update_pen(pen_id, payload)
                        st.success("Pen updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with tab_add:
        with st.form("add_pen"):
            name = st.text_input("Pen Name *", placeholder="Finishing-3")
            capacity = st.number_input("Capacity *", min_value=1, value=20, step=1)
            pen_type = st.text_input("Type", placeholder="finishing, nursery, farrowing...")
            submitted = st.form_submit_button("➕ Add Pen")

        if submitted:
            if not name.strip():
                st.warning("Pen name is required.")
            else:
                try:
                    api.create_pen({"name": name.strip(), "capacity": capacity, "pen_type": pen_type or None})
                    st.success(f"Pen '{name}' created!")
                except Exception as e:
                    st.error(str(e))
