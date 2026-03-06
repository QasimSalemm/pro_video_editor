import os
import streamlit as st

def get_fonts():
    """Scan the 'fonts' directory for .ttf files."""
    FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
    fonts = {}
    if os.path.exists(FONTS_DIR):
        font_files = [f for f in os.listdir(FONTS_DIR) if f.lower().endswith((".ttf",))]
        fonts = {os.path.splitext(f)[0]: os.path.join(FONTS_DIR, f) for f in font_files}
    return fonts

def render_preview_controls(width_key, height_key, title="Preview Monitor", expanded=False, default_width=50):
    """
    Renders only the controls for the preview monitor.
    Returns: (width_pct, height_px)
    """
    with st.expander(f"{title} Controls", expanded=expanded):
        w_pct = st.slider("Scale Width (%)", 10, 100, default_width, step=5, key=width_key)
        h_px = st.number_input("Fixed Height (px) [0=Auto]", 0, 2000, 0, step=50, key=height_key)
        st.caption("💡 Adjust scaling for the view below.")
    return w_pct, h_px

def render_preview_video(video_element, w_pct, h_px, title="Preview Monitor", caption_text=None):
    """
    Renders only the video display part of the preview monitor.
    """
    # Centered Display Logic
    margin = (100 - w_pct) / 200.0
    if margin > 0:
        c_l, c_mid, c_r = st.columns([margin, w_pct/100.0, margin])
    else:
        c_mid = st.container()
        
    with c_mid:
        if title:
            st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
            
        st.video(video_element)
        if caption_text:
            st.caption(caption_text)

def render_preview_monitor(video_element, width_key, height_key, title="Preview Monitor", caption_text=None, default_width=50):
    """
    Renders a unified preview monitor with scaling controls (Legacy Wrapper).
    """
    w_pct, h_px = render_preview_controls(width_key, height_key, title, False, default_width)
    render_preview_video(video_element, w_pct, h_px, title, caption_text)
    return w_pct, h_px

def render_final_presentation(file_path, width_key, height_key, download_label, reset_callback, reset_label="Start New"):
    """
    Renders the persistent 'Master Presentation' block after processing is done.
    """
    if file_path and os.path.exists(file_path):
        
        # Row 1: Controls (Left) & Video (Right)
        col1, col2 = st.columns([0.35, 0.65])
        
        with col1:
            # Using the new separate control function
            w_pct, h_px = render_preview_controls(width_key, height_key, "Master Presentation", True)
        
        with col2:
            # Using the new separate video function
            render_preview_video(file_path, w_pct, h_px, None) # No title on video side to keep it clean

        # Row 2: Actions
        act1, act2 = st.columns(2)
        with act1:
            with open(file_path, "rb") as f:
                st.download_button(download_label, f, file_name=os.path.basename(file_path), use_container_width=True, type="primary")
        with act2:
            if st.button(reset_label, key=f"btn_reset_{width_key}", use_container_width=True):
                reset_callback()
                st.rerun()
