import os
import sys
import time
import tempfile
from random import randint
import streamlit as st
import utility_functions as uf

# Import new modules
from tabs.trim import render_trim_tab
from tabs.merge import render_merge_tab
from tabs.media_overlay import render_media_overlay_tab
import tabs.info_pages as info_pages

# ==============================
# Streamlit Page Config
# ==============================
st.set_page_config(
    page_title="Video Editor - All-in-One",
    page_icon="images/subtitles_theme.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize workspace folders
uf.init_workspace(["temp_uploads", "temp_outputs"])

# Auto-cleanup orphaned files older than 2 hours (7200 seconds)
def auto_cleanup(threshold=7200):
    for folder in ["temp_uploads", "temp_outputs"]:
        if os.path.exists(folder):
            now = time.time()
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.stat(fp).st_mtime < (now - threshold):
                    try:
                        os.remove(fp)
                    except: pass

auto_cleanup()

# ==============================
# Session State & Navigation
# ==============================
if "reset_key" not in st.session_state: st.session_state.reset_key = 0
if "session_id" not in st.session_state: st.session_state.session_id = f"sess_{int(time.time())}_{randint(0, 100000)}"
if "mt_overlays" not in st.session_state: st.session_state.mt_overlays = []
if "mt_edit_index" not in st.session_state: st.session_state.mt_edit_index = None
if "mt_bulk_df" not in st.session_state: st.session_state.mt_bulk_df = None

# Navigation State
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Video Editor"

# Studio Widget Defaults
if "mt_txt_input" not in st.session_state: st.session_state.mt_txt_input = ""
if "mt_s_t" not in st.session_state: st.session_state.mt_s_t = 0.0
if "mt_e_t" not in st.session_state: st.session_state.mt_e_t = 5.0
if "mt_f_fam" not in st.session_state: st.session_state.mt_f_fam = "Arial"
if "mt_f_size" not in st.session_state: st.session_state.mt_f_size = 20
if "mt_pos" not in st.session_state: st.session_state.mt_pos = "Bottom center"
if "mt_x_pct" not in st.session_state: st.session_state.mt_x_pct = 50
if "mt_y_pct" not in st.session_state: st.session_state.mt_y_pct = 90
if "mt_t_col" not in st.session_state: st.session_state.mt_t_col = "#000000"
if "mt_b_col" not in st.session_state: st.session_state.mt_b_col = "#FFFEFF"
if "mt_b_opac" not in st.session_state: st.session_state.mt_b_opac = 0.50
if "mt_pad" not in st.session_state: st.session_state.mt_pad = 10
if "mt_edit_mode" not in st.session_state: st.session_state.mt_edit_mode = "Text Overlays"
if "mt_final_out_path" not in st.session_state: st.session_state.mt_final_out_path = None
if "merge_final_out_path" not in st.session_state: st.session_state.merge_final_out_path = None
if "trim_final_out_path" not in st.session_state: st.session_state.trim_final_out_path = None


# ==============================
# Sidebar Navigation & Settings
# ==============================
st.sidebar.title("Video Editor")

# Navigation Menu
with st.sidebar.expander("Help & Info", expanded=False):
    nav_options = [
        "Contact", 
        "Privacy Policy", 
        "Terms & Conditions", 
        "Guide: Video Tools", 
        "Guide: Subtitles"
    ]
    
    # Determine proper index based on current state
    try:
        def_idx = nav_options.index(st.session_state.app_mode)
    except ValueError:
        def_idx = None # Default to None if "Video Editor" or unknown

    def on_nav_change():
        st.session_state.app_mode = st.session_state.nav_radio
    
    st.radio("Go to:", nav_options, index=def_idx, key="nav_radio", on_change=on_nav_change)

# Button to return to Editor
if st.session_state.app_mode != "Video Editor":
    if st.sidebar.button("Back to Editor", use_container_width=True, type="primary"):
        st.session_state.app_mode = "Video Editor"
        st.rerun()

# Global Settings (Only show in Editor mode)
if st.session_state.app_mode == "Video Editor":

    st.sidebar.header("Global Settings")
    codec = st.sidebar.selectbox("Video Codec", ["libx264", "mpeg4", "libvpx"], index=0)
    audio_codec = st.sidebar.selectbox("Audio Codec", ["aac", "libvorbis", "mp3"], index=0)

    with st.sidebar.expander("Pro Settings (Speed)"):
        render_preset = st.selectbox("Encoding Speed", ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"], index=0, help="Faster = lower quality/larger file size. Slower = better quality/smaller file.")
        render_threads = st.number_input("Threads", 1, 16, 4, help="Number of CPU threads to use for rendering.")
        merge_method = st.selectbox("Merging Strategy", ["compose", "chain"], index=0, help="'Compose' is slower but handles different resolutions. 'Chain' is much faster but requires identical video properties.")

    st.sidebar.header("Maintenance")
    if st.sidebar.button("Reset Project", type="secondary", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.mt_overlays = []
        uf.cleanup_workspace(["temp_uploads", "temp_outputs"])
        st.toast("Project reset! Workspace cleaned.")
        st.rerun()

# ==============================
# Main Content Routing
# ==============================
if st.session_state.app_mode == "Video Editor":
    st.title("Video Editor")
    
    with st.expander("Welcome to Video Editor - Quick Start Guide", expanded=False):
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.markdown("""
            ### Core Capabilities
            - **Trim & Subclip**: Cut segments with millisecond precision.
            - **Merge Videos**: Join multiple clips into a single masterpiece.
            - **Music & Text**: Add soundtracks and styled overlays manually.
            - **Batch Subtitles**: Process hundreds of subtitles via CSV/XLSX.
            """)
        with col2:
            st.markdown("""
            ### Privacy & Speed
            - All processing happens in local `temp` folders.
            - Files are automatically wiped on Reset or after 2 hours.
            """)
        st.info("💡 Tip: Use 'Pro Settings' in the sidebar to boost rendering speed!")

    # Main Tabs
    tab_trim, tab_merge, tab_music_text = st.tabs([
        "Trim & Subclip", 
        "Merge Videos", 
        "Music & Text"
    ])

    # --- ✂️ Trim Tab ---
    with tab_trim:
        render_trim_tab(codec, audio_codec, render_preset, render_threads)

    # --- 🔗 Merge Tab ---
    with tab_merge:
        render_merge_tab(codec, audio_codec, render_preset, render_threads, merge_method)

    # --- 🎵 Add Music & Text Tab ---
    with tab_music_text:
        render_media_overlay_tab(codec, audio_codec, render_preset, render_threads)

elif st.session_state.app_mode == "Contact":
    info_pages.render_contact()

elif st.session_state.app_mode == "Privacy Policy":
    info_pages.render_privacy_policy()

elif st.session_state.app_mode == "Terms & Conditions":
    info_pages.render_terms_conditions()

elif st.session_state.app_mode == "Guide: Video Tools":
    info_pages.render_guide_video_tools()

elif st.session_state.app_mode == "Guide: Subtitles":
    info_pages.render_guide_subtitles()

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: grey; font-size: 0.8rem;'>Video Editor - Powered by Qasim Saleem</div>", unsafe_allow_html=True)



