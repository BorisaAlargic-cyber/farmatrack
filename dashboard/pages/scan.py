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


def _do_lookup(tag: str, key_suffix: str):
    """Run scan_text and store result in session state."""
    try:
        res = api.scan_text(tag)
        st.session_state[f"_lookup_{key_suffix}"] = {"tag": tag, "res": res}
    except Exception as e:
        st.error(str(e))


def _show_lookup_result(key_suffix: str):
    """Render stored lookup result — called on every rerun so buttons persist."""
    data = st.session_state.get(f"_lookup_{key_suffix}")
    if not data:
        return
    tag = data["tag"]
    res = data["res"]

    if res.get("pig_id"):
        st.success(res["message"])
        try:
            pig_card(api.get_pig(res["pig_id"]))
        except Exception:
            pass
    else:
        st.warning(f"Tag **`{tag}`** is not registered yet.")
        if st.button("➕ Register this pig", type="primary", key=f"reg_{key_suffix}_{tag}"):
            _register_dialog(tag)


def render():
    st.title("📷 Scan Ear Tag")

    tab_camera, tab_text, tab_img, tab_logs = st.tabs(
        ["📸 Camera", "✏️ Manual Entry", "🖼 Image Upload", "📋 Scan Logs"]
    )

    # ── Live camera ────────────────────────────────────────
    with tab_camera:
        photo = st.camera_input("Take a photo of the ear tag")

        if photo is not None:
            photo_key = hash(photo.getvalue())
            if st.session_state.get("_cam_key") != photo_key:
                with st.spinner("Reading tag..."):
                    try:
                        from scanner.ocr import ocr_image
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(photo.getvalue())
                            tmp_path = tmp.name
                        try:
                            raw_text = ocr_image(tmp_path) or ""
                        finally:
                            os.unlink(tmp_path)
                        from services.scan_service import parse_tag
                        parsed, _ = parse_tag(raw_text or "")
                        st.session_state["_cam_key"] = photo_key
                        st.session_state["_cam_ocr"] = parsed or ""
                        st.session_state.pop("_lookup_cam", None)
                    except Exception:
                        st.session_state["_cam_key"] = photo_key
                        st.session_state["_cam_ocr"] = ""

            ocr_guess = st.session_state.get("_cam_ocr", "")
            st.info(
                "OCR pre-fills the field below — check the photo and correct the number if needed, "
                "then click **Look Up**."
            )
            tag_input = st.text_input(
                "Tag number", value=ocr_guess, placeholder="e.g. 2419",
                key=f"cam_tag_{photo_key}",
            )
            if st.button("🔍 Look Up", type="primary", key="cam_lookup"):
                if not tag_input.strip():
                    st.warning("Enter the tag number from the photo.")
                else:
                    _do_lookup(tag_input.strip(), key_suffix="cam")

            _show_lookup_result("cam")

    # ── Manual entry ───────────────────────────────────────
    with tab_text:
        raw = st.text_input("Enter tag number", placeholder="2419 or SOW-001")
        if st.button("🔍 Look Up", key="btn_text"):
            if not raw.strip():
                st.warning("Please enter a tag number.")
            else:
                _do_lookup(raw.strip(), key_suffix="txt")

        _show_lookup_result("txt")

    # ── Image upload ───────────────────────────────────────
    with tab_img:
        uploaded = st.file_uploader("Upload ear-tag photo", type=["png", "jpg", "jpeg"])
        if uploaded is not None:
            photo_key_u = hash(uploaded.getvalue())
            if st.session_state.get("_img_key") != photo_key_u:
                with st.spinner("Reading tag..."):
                    try:
                        res = api.scan_image(uploaded.getvalue(), uploaded.name)
                        st.session_state["_img_key"] = photo_key_u
                        st.session_state["_img_result"] = res
                        st.session_state.pop("_lookup_img", None)
                    except Exception as e:
                        st.session_state["_img_result"] = None
                        st.error(str(e))

            res = st.session_state.get("_img_result")
            if res:
                ocr_guess_u = res.get("parsed_tag") or ""
                tag_input_u = st.text_input(
                    "Tag number (correct if needed)",
                    value=ocr_guess_u,
                    placeholder="e.g. 2419",
                    key=f"img_tag_{photo_key_u}",
                )
                if st.button("🔍 Look Up", type="primary", key="img_lookup"):
                    if tag_input_u.strip():
                        _do_lookup(tag_input_u.strip(), key_suffix="img")

                _show_lookup_result("img")

                if res.get("raw_text"):
                    with st.expander("Raw OCR output"):
                        st.code(res["raw_text"])

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
