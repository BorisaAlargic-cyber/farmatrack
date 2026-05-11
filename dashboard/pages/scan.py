"""Scan page — manual text entry, live camera, or image upload for ear-tag recognition."""

import streamlit as st
from dashboard import api_client as api
from dashboard.components.pig_card import pig_card


def render():
    st.title("📷 Scan Ear Tag")

    tab_camera, tab_text, tab_img, tab_logs = st.tabs(["📸 Live Camera", "Manual Entry", "Image Upload", "Scan Logs"])

    # ── Live camera scan ───────────────────────────────────
    with tab_camera:
        st.info("Point your camera at the ear tag and take a photo — it scans automatically.")
        photo = st.camera_input("Take a photo of the ear tag")
        if photo is not None:
            with st.spinner("Scanning..."):
                try:
                    res = api.scan_image(photo.getvalue(), "camera.jpg")
                    _show_result(res)
                except Exception as e:
                    st.error(str(e))

    # ── Manual text scan ───────────────────────────────────
    with tab_text:
        raw = st.text_input("Enter ear tag or raw OCR text", placeholder="SOW-001")
        if st.button("🔍 Scan", key="btn_text"):
            if not raw.strip():
                st.warning("Please enter text.")
            else:
                try:
                    res = api.scan_text(raw.strip())
                    _show_result(res)
                except Exception as e:
                    st.error(str(e))

    # ── Image upload scan ──────────────────────────────────
    with tab_img:
        uploaded = st.file_uploader("Upload ear-tag photo", type=["png", "jpg", "jpeg"])
        if uploaded and st.button("📸 Scan Image", key="btn_img"):
            try:
                res = api.scan_image(uploaded.getvalue(), uploaded.name)
                _show_result(res)
            except Exception as e:
                st.error(str(e))

    # ── Logs ───────────────────────────────────────────────
    with tab_logs:
        try:
            logs = api.list_scan_logs()
            if logs:
                import pandas as pd
                df = pd.DataFrame(logs)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No scan logs yet.")
        except Exception as e:
            st.error(str(e))


def _show_result(res: dict):
    st.markdown(f"**Message:** {res['message']}")
    if res.get("parsed_tag"):
        st.markdown(f"**Parsed tag:** `{res['parsed_tag']}` — confidence {res.get('confidence', '?')}")
    if res.get("pig_id"):
        try:
            pig = api.get_pig(res["pig_id"])
            pig_card(pig)
        except Exception:
            pass
