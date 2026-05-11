"""Herd management page — list, filter, add, edit pigs."""

import streamlit as st
import pandas as pd
from dashboard import api_client as api
from dashboard.components.pig_card import pig_card

CATEGORIES = ["", "piglet", "finisher", "gilt", "sow"]


def render():
    st.title("🐖 Herd Management")

    tab_list, tab_add = st.tabs(["Browse Herd", "Add Pig"])

    # ── Browse / filter ────────────────────────────────────
    with tab_list:
        c1, c2, c3 = st.columns(3)
        with c1:
            cat_filter = st.selectbox("Category", CATEGORIES, format_func=lambda x: x.capitalize() if x else "All")
        with c2:
            try:
                pens = api.list_pens()
                pen_opts = {0: "All"} | {p["id"]: p["name"] for p in pens}
            except Exception:
                pen_opts = {0: "All"}
            pen_filter = st.selectbox("Pen", list(pen_opts.keys()), format_func=lambda x: pen_opts[x])
        with c3:
            active_only = st.checkbox("Active only", value=True)

        try:
            pigs = api.list_pigs(
                category=cat_filter or None,
                pen_id=pen_filter if pen_filter else None,
                active_only=active_only,
            )
        except Exception as e:
            st.error(str(e))
            return

        st.caption(f"{len(pigs)} pig(s) found")

        if pigs:
            df = pd.DataFrame(pigs)
            cols_show = ["id", "ear_tag", "category", "breed", "weight_kg", "pen_id", "is_active"]
            st.dataframe(df[[c for c in cols_show if c in df.columns]], use_container_width=True, hide_index=True)

            selected_id = st.number_input("Enter Pig ID to view details", min_value=0, value=0, step=1)
            if selected_id:
                try:
                    pig = api.get_pig(selected_id)
                    pig_card(pig)

                    with st.expander("Edit this pig"):
                        new_weight = st.number_input("Weight (kg)", value=pig.get("weight_kg") or 0.0, step=0.1)
                        new_notes = st.text_area("Notes", value=pig.get("notes") or "")
                        new_active = st.checkbox("Active", value=pig.get("is_active", True))
                        if st.button("💾 Save Changes"):
                            api.update_pig(selected_id, {"weight_kg": new_weight, "notes": new_notes, "is_active": new_active})
                            st.success("Updated!")
                            st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            st.info("No pigs match your filters.")

    # ── Add pig ────────────────────────────────────────────
    with tab_add:
        with st.form("add_pig"):
            ear_tag = st.text_input("Ear Tag *", placeholder="SOW-009")
            category = st.selectbox("Category *", CATEGORIES[1:])
            breed = st.text_input("Breed")
            dob = st.date_input("Date of Birth", value=None)
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
            try:
                pens_list = api.list_pens()
                pen_map = {p["id"]: p["name"] for p in pens_list}
            except Exception:
                pen_map = {}
            pen_id = st.selectbox("Pen", [None] + list(pen_map.keys()), format_func=lambda x: pen_map.get(x, "— None —"))
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("➕ Add Pig")

        if submitted:
            if not ear_tag.strip():
                st.warning("Ear tag is required.")
            else:
                payload = {
                    "ear_tag": ear_tag.strip(),
                    "category": category,
                    "breed": breed or None,
                    "date_of_birth": str(dob) if dob else None,
                    "weight_kg": weight or None,
                    "pen_id": pen_id,
                    "notes": notes or None,
                }
                try:
                    api.create_pig(payload)
                    st.success(f"Pig {ear_tag} added!")
                except Exception as e:
                    st.error(str(e))
