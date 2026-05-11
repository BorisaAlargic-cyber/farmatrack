"""Scan page — live camera, manual entry, or image upload for ear-tag recognition."""

import streamlit as st
from dashboard import api_client as api
from dashboard.components.pig_card import pig_card


@st.dialog("🐷 Register New Pig")
def _register_dialog(ear_tag: str):
    st.markdown(f"Scanned tag: **`{ear_tag}`**")
    st.divider()

    category = st.selectbox(
        "Category *",
        ["piglet", "finisher", "gilt", "sow"],
        format_func=lambda x: {
            "piglet": "🐷 Piglet",
            "finisher": "🥩 Finisher (regular pig)",
            "gilt": "🐖 Gilt (young female, not yet farrowed)",
            "sow": "🐷 Sow (farrowing)",
        }[x],
    )

    pen_id = None
    try:
        pens = api.list_pens()
        if pens:
            pen_map = {p["name"]: p["id"] for p in pens}
            sel = st.selectbox("Pen (optional)", ["— None —"] + list(pen_map))
            if sel != "— None —":
                pen_id = pen_map[sel]
    except Exception:
        pass

    if st.button("✅ Register Pig", type="primary", use_container_width=True):
        try:
            pig = api.create_pig({"ear_tag": ear_tag, "category": category, "pen_id": pen_id})
            st.success(f"Registered **{pig['ear_tag']}** as {category}!")
            st.caption("Close this dialog and scan again to view the pig profile.")
        except Exception as e:
            st.error(str(e))


def render():
    st.title("📷 Scan Ear Tag")

    tab_camera, tab_text, tab_img, tab_logs = st.tabs(
        ["📸 Live Camera", "✏️ Manual Entry", "🖼 Image Upload", "📋 Scan Logs"]
    )

    # ── Live camera ────────────────────────────────────────
    with tab_camera:
        st.info("Point your camera at the ear tag and take a photo.")
        photo = st.camera_input("Take a photo of the ear tag")
        if photo is not None:
            # Cache result so button clicks don't retrigger the slow OCR scan
            photo_key = hash(photo.getvalue())
            if st.session_state.get("_cam_key") != photo_key:
                with st.spinner("Scanning..."):
                    try:
                        res = api.scan_image(photo.getvalue(), "camera.jpg")
                        st.session_state["_cam_key"] = photo_key
                        st.session_state["_cam_result"] = res
                    except Exception as e:
                        st.session_state["_cam_result"] = None
                        st.error(str(e))
            res = st.session_state.get("_cam_result")
            if res:
                _show_result(res, key_suffix="cam")

    # ── Manual entry ───────────────────────────────────────
    with tab_text:
        raw = st.text_input("Enter ear tag number", placeholder="9142 or SOW-001")
        if st.button("🔍 Look up", key="btn_text"):
            if not raw.strip():
                st.warning("Please enter a tag number.")
            else:
                try:
                    res = api.scan_text(raw.strip())
                    _show_result(res, key_suffix="txt")
                except Exception as e:
                    st.error(str(e))

    # ── Image upload ───────────────────────────────────────
    with tab_img:
        uploaded = st.file_uploader("Upload ear-tag photo", type=["png", "jpg", "jpeg"])
        if uploaded and st.button("📸 Scan Image", key="btn_img"):
            try:
                res = api.scan_image(uploaded.getvalue(), uploaded.name)
                _show_result(res, key_suffix="img")
            except Exception as e:
                st.error(str(e))

    # ── Scan logs ──────────────────────────────────────────
    with tab_logs:
        try:
            logs = api.list_scan_logs()
            if logs:
                import pandas as pd
                st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
            else:
                st.info("No scan logs yet.")
        except Exception as e:
            st.error(str(e))


def _show_result(res: dict, key_suffix: str = ""):
    if res.get("pig_id"):
        st.success(res["message"])
        try:
            pig_card(api.get_pig(res["pig_id"]))
        except Exception:
            pass

    elif res.get("parsed_tag"):
        tag = res["parsed_tag"]
        st.warning(f"Tag **`{tag}`** is not registered in the system yet.")
        if st.button("➕ Register this pig", type="primary", key=f"reg_{key_suffix}_{tag}"):
            _register_dialog(tag)

    else:
        st.error(res["message"])

    if res.get("raw_text") and not res.get("pig_id"):
        with st.expander("Raw OCR output (debug)"):
            st.code(res["raw_text"])
