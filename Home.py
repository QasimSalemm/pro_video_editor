import os
import sys
import time
import tempfile
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, ImageClip, CompositeVideoClip
import utility_functions as uf
import image_generator as ig
import position_helpers as ph
import streamlit_logger as sl

# ==============================
# Streamlit Page Config
# ==============================
st.set_page_config(
    page_title="Mega Video Editor - All-in-One",
    page_icon="🎬",
    layout="wide"
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
# Session State Initialization
# ==============================
if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
if "mt_overlays" not in st.session_state:
    st.session_state.mt_overlays = []

st.title("🎬 Mega Video Editor")

with st.expander("👋 Welcome to Mega Video Editor - Quick Start Guide", expanded=False):
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.markdown("""
        ### 🛠️ Core Capabilities
        - **Trim & Subclip**: Cut segments with millisecond precision.
        - **Merge Videos**: Join multiple clips into a single masterpiece.
        - **Music & Text**: Add soundtracks and styled overlays manually.
        - **Batch Subtitles**: Process hundreds of subtitles via CSV/XLSX.
        """)
    with col2:
        st.markdown("""
        ### 🔒 Privacy & Speed
        - All processing happens in local `temp` folders.
        - Files are automatically wiped on Reset or after 2 hours.
        - Multi-threaded rendering for **Max Speed**.
        """)
    st.info("💡 Tip: Use 'Pro Settings' in the sidebar to boost rendering speed!")

st.divider()

# ==============================
# Sidebar Settings
# ==============================
st.sidebar.header("⚙️ Global Settings")
codec = st.sidebar.selectbox("Video Codec", ["libx264", "mpeg4", "libvpx"], index=0)
audio_codec = st.sidebar.selectbox("Audio Codec", ["aac", "libvorbis", "mp3"], index=0)

with st.sidebar.expander("⚡ Pro Settings (Speed)"):
    render_preset = st.selectbox("Encoding Speed", ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"], index=0, help="Faster = lower quality/larger file size. Slower = better quality/smaller file.")
    render_threads = st.number_input("Threads", 1, 16, 4, help="Number of CPU threads to use for rendering.")
    merge_method = st.selectbox("Merging Strategy", ["compose", "chain"], index=0, help="'Compose' is slower but handles different resolutions. 'Chain' is much faster but requires identical video properties.")

st.sidebar.divider()
st.sidebar.header("🧹 Maintenance")
if st.sidebar.button("🗑️ Reset Project & Clear Files", type="secondary", use_container_width=True):
    st.session_state.reset_key += 1
    st.session_state.mt_overlays = []
    # Fully purge temp folders
    uf.cleanup_workspace(["temp_uploads", "temp_outputs"])
    st.toast("Project reset! Workspace cleaned.")
    st.rerun()

# ==============================
# Helper Functions
# ==============================
def get_fonts():
    FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
    fonts = {}
    if os.path.exists(FONTS_DIR):
        font_files = [f for f in os.listdir(FONTS_DIR) if f.lower().endswith((".ttf",))]
        fonts = {os.path.splitext(f)[0]: os.path.join(FONTS_DIR, f) for f in font_files}
    return fonts

def apply_text_overlays(video_clip, overlays, font_path):
    text_clips = []
    for ov in overlays:
        img_path = ig.create_text_overlay_image(
            ov["text"], font_path=font_path, font_size=ov["font_size"],
            text_color=tuple(int(ov["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)),
            bg_color=ov["bg_color"], bg_opacity=ov["bg_opacity"], padding=ov["padding"]
        )
        np_img = np.array(Image.open(img_path))
        if np_img.shape[-1] == 4:
            rgb = np_img[:, :, :3]
            alpha = np_img[:, :, 3] / 255.0
            rgb_clip = ImageClip(rgb)
            mask_clip = ImageClip(alpha, ismask=True)
            img_clip = rgb_clip.set_mask(mask_clip)
        else:
            img_clip = ImageClip(np_img)

        pos = ov["position"]
        if pos == "Custom (percent)":
            ov_w, ov_h = Image.open(img_path).size
            x_px, y_px = ph.compute_custom_xy_percent(video_clip.w, video_clip.h, ov_w, ov_h, ov["x_percent"], ov["y_percent"])
            img_clip = img_clip.set_position((x_px, y_px))
        else:
            img_clip = img_clip.set_position(ph.PRESET_POSITIONS[pos])

        img_clip = img_clip.set_start(ov["start"]).set_duration(max(0.1, ov["end"] - ov["start"]))
        text_clips.append(img_clip)
    
    final = CompositeVideoClip([video_clip] + text_clips)
    final.fps = video_clip.fps
    return final, text_clips

# ==============================
# Main Tabs
# ==============================
tab_trim, tab_merge, tab_music_text, tab_batch = st.tabs([
    "✂️ Trim & Subclip", 
    "🔗 Merge Videos", 
    "🎵 Music & Text", 
    "📜 Batch Subtitles"
])

# --- ✂️ Trim Tab ---
with tab_trim:
    st.header("✂️ Trim Video")
    st.info("Upload a video and select the start/end search to cut a specific segment.")
    
    video_file = st.file_uploader("Choose Video", type=["mp4","mov","avi"], key=f"trim_{st.session_state.reset_key}")
    
    if video_file:
        video_path = uf.save_temp_file(video_file, ".mp4")
        video = VideoFileClip(video_path)
        
        # UI: Layout for Configuration and Preview
        conf_col, prev_col = st.columns([0.65, 0.35])
        
        with conf_col:
            st.subheader("⏱️ Trim Configuration")
            with st.container(border=True):
                c1, c2 = st.columns(2)
                start = c1.number_input("Start Time (sec)", 0.0, video.duration, 0.0, step=0.1, key="t_start")
                end = c2.number_input("End Time (sec)", 0.0, video.duration, min(5.0, video.duration), step=0.1, key="t_end")
                
                # Sub-metric for selection length
                sel_len = max(0.0, end - start)
                st.info(f"✨ Selection: `{sel_len:.2f}s` | Original: `{video.duration:.2f}s`", icon="⏱️")

        with prev_col:
            st.subheader("📺 Source Video")
            st.video(video_file)

        st.divider()
        
        if st.button("🚀 Generate Subclip", type="primary", use_container_width=True):
            if start < end:
                st.write("🎬 **Processing subclip...**")
                sub = video.subclip(start, end)
                out_name = os.path.join("temp_outputs", f"Trimmed_{datetime.now().strftime('%H%M%S')}.mp4")
                sub.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(sub.fps*sub.duration)))
                
                st.success("🎉 **Success! Your subclip is ready.**")
                with st.container(border=True):
                    res_col1, res_col2 = st.columns([0.7, 0.3])
                    with res_col1:
                        with st.expander("👁️ Preview Result", expanded=True):
                            st.video(out_name)
                    with res_col2:
                        st.markdown("#### 📥 Actions")
                        with open(out_name, "rb") as f:
                            st.download_button("Download MP4", f, file_name=os.path.basename(out_name), use_container_width=True, type="primary")
                        if st.button("🗑️ Clear Result", key="clear_trim"):
                            uf.remove_temp_files(out_name)
                            st.rerun()
                
                sub.close()
                video.close()
            else:
                st.error("Error: End time must be greater than start time.")

# --- 🔗 Merge Tab ---
with tab_merge:
    st.header("🔗 Concatenate Videos")
    st.info("Upload multiple video files to merge them into a single video in the order they appear.")
    
    files = st.file_uploader("Choose Videos to Merge", type=["mp4","mov","avi"], accept_multiple_files=True, key=f"merge_{st.session_state.reset_key}")
    
    if files:
        st.subheader("📂 Selected Files")
        clips = []
        # Create a clean list with metrics
        for i, f in enumerate(files):
            p = uf.save_temp_file(f, ".mp4")
            c = VideoFileClip(p)
            clips.append(c)
            with st.container(border=True):
                col_a, col_b = st.columns([0.1, 0.9])
                col_a.write(f"#{i+1}")
                col_b.write(f"**{f.name}** | Duration: `{c.duration:.2f}s` | Resolution: `{c.w}x{c.h}`")
        
        st.divider()
        if st.button("🚀 Merge All Now", type="primary", use_container_width=True):
            if len(clips) >= 2:
                st.write(f"🔗 **Merging clips using '{merge_method}' method... Please wait.**")
                final = concatenate_videoclips(clips, method=merge_method)
                out_name = os.path.join("temp_outputs", f"Merged_{datetime.now().strftime('%H%M%S')}.mp4")
                final.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(final.fps*final.duration)))
                
                st.success("🎉 **Success! Videos merged into one.**")
                with st.container(border=True):
                    res_col1, res_col2 = st.columns([0.7, 0.3])
                    with res_col1:
                        with st.expander("👁️ Preview Result", expanded=True):
                            st.video(out_name)
                    with res_col2:
                        st.markdown("#### 📥 Actions")
                        with open(out_name, "rb") as f:
                            st.download_button("Download Combined", f, file_name=os.path.basename(out_name), use_container_width=True, type="primary")
                        if st.button("🗑️ Clear Result", key="clear_merge"):
                            uf.remove_temp_files(out_name)
                            st.rerun()
                uf.close_and_remove(final, *clips)
            else:
                st.warning("Please upload at least 2 videos to merge.")

# --- 🎵 Add Music & Text Tab ---
with tab_music_text:
    st.header("🎵 Integrated Editor")
    st.info("Combine video, background music, and multiple text overlays in three easy steps.")
    
    # --- Step 1: Sources ---
    st.subheader("Step 1: Upload Sources")
    col1, col2 = st.columns(2)
    v_file = col1.file_uploader("Upload Base Video", type=["mp4","mov","avi"], key=f"mt_v_{st.session_state.reset_key}")
    a_file = col2.file_uploader("Add Background Music (Optional)", type=["mp3","wav"], key=f"mt_a_{st.session_state.reset_key}")
    
    if v_file:
        v_path = uf.save_temp_file(v_file, ".mp4")
        video = VideoFileClip(v_path)
        
        # Split view for settings and preview
        src_col1, src_col2 = st.columns([0.65, 0.35])
        
        with src_col2:
            st.subheader("📺 Source Preview")
            st.video(v_file)
        
        with src_col1:
            st.metric("Base Video Duration", f"{video.duration:.2f}s")
            
            # --- Step 2: Audio Mix ---
            st.divider()
            st.subheader("Step 2: Audio Configuration")
            with st.container(border=True):
                v_vol_col, a_vol_col = st.columns(2)
                v_vol = v_vol_col.slider("Original Video Volume", 0.0, 1.0, 1.0, 0.05)
                if a_file:
                    a_vol = a_vol_col.slider("New Music Volume", 0.0, 1.0, 0.5, 0.05)
                    a_path = uf.save_temp_file(a_file, ".mp3")
                    audio = AudioFileClip(a_path)
                
                    # Audio Trimming & Timing
                    st.markdown("🔍 **Audio Timing Control**")
                    at1, at2, at3 = st.columns(3)
                    a_start = at1.number_input("Audio Start (s)", 0.0, audio.duration, 0.0, step=0.1)
                    a_end = at2.number_input("Audio End (s)", 0.0, audio.duration, audio.duration, step=0.1)
                    v_start = at3.number_input("Start on Video (s)", 0.0, video.duration, 0.0, step=0.1)
                    
                    a_sel_len = max(0.1, a_end - a_start)
                    st.write(f"🎵 **Playing:** `{a_sel_len:.2f}s` of audio starting at `{v_start}s` on video.")
                else:
                    a_vol = 0.0
                    audio = None
                    a_start, a_end, v_start = 0, 0, 0
                    a_vol_col.info("No music file uploaded.")

        # --- Step 3: Text Overlays ---
        st.divider()
        st.subheader("Step 3: Text Overlay Management")
        
        # Split into Adder (Left) and Manager (Right)
        add_col, list_col = st.columns([0.45, 0.55])
        
        if "mt_overlays" not in st.session_state:
            st.session_state.mt_overlays = []
            
        with add_col:
            st.markdown("#### ➕ Add New Overlay")
            with st.container(border=True):
                txt = st.text_area("Text Content", placeholder="Type your message here...", key="mt_txt_input")
                t1, t2 = st.columns(2)
                s_t = t1.number_input("Start (s)", 0.0, video.duration, 0.0, step=0.5, key="mt_s_t")
                e_t = t2.number_input("End (s)", 0.0, video.duration, min(5.0, video.duration), step=0.5, key="mt_e_t")
                
                with st.expander("🎨 Style & Position Settings"):
                    f_col1, f_col2 = st.columns(2)
                    fonts = get_fonts()
                    sel_font = f_col1.selectbox("Font Family", list(fonts.keys()) if fonts else ["Arial"], key="mt_f_fam")
                    f_size = f_col2.number_input("Font Size", 10, 200, 30, key="mt_f_size")
                    
                    p_col1, p_col2 = st.columns(2)
                    pos = p_col1.selectbox("Position", ["Bottom center", "Top center", "Center", "Top-left", "Top-right", "Bottom-left", "Bottom-right", "Custom (percent)"], key="mt_pos")
                    p_pad = p_col2.number_input("Padding (px)", 0, 100, 15, key="mt_pad")
                    
                    x_pct, y_pct = 50, 90
                    if pos == "Custom (percent)":
                        px1, px2 = st.columns(2)
                        x_pct = px1.slider("Horizontal %", 0, 100, 50, key="mt_x_pct")
                        y_pct = px2.slider("Vertical %", 0, 100, 90, key="mt_y_pct")
                    
                    c_col1, c_col2 = st.columns(2)
                    t_color = c_col1.color_picker("Text Color", "#FFFFFF", key="mt_t_col")
                    b_color = c_col2.color_picker("BG Color", "#000000", key="mt_b_col")
                    b_opac = st.slider("BG Opacity", 0.0, 1.0, 0.7, key="mt_b_opac")
                
                if st.button("➕ Add Overlay to Project", use_container_width=True):
                    if txt.strip():
                        st.session_state.mt_overlays.append({
                            "text": txt, "start": s_t, "end": e_t, "font_size": f_size,
                            "color": t_color, "bg_color": tuple(int(b_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)),
                            "bg_opacity": b_opac, "padding": p_pad, "position": pos,
                            "x_percent": x_pct, "y_percent": y_pct 
                        })
                        st.toast("Updated Project List!")
                        st.rerun()

        with list_col:
            st.markdown("#### 📋 Current Overlays List")
            if st.session_state.mt_overlays:
                # Iterate in reverse to show newest first? Or standard order for timeline feel.
                for i, o in enumerate(st.session_state.mt_overlays):
                    with st.container(border=True):
                        c_a, c_b = st.columns([0.85, 0.15])
                        c_a.markdown(f"**{i+1}.** {o['text']} <br><small>`{o['start']}s` — `{o['end']}s` | {o['position']}</small>", unsafe_allow_html=True)
                        if c_b.button("🗑️", key=f"del_mt_{i}", help="Delete this overlay"):
                            st.session_state.mt_overlays.pop(i)
                            st.rerun()
                if st.button("🗑️ Clear All Overlays", type="secondary", use_container_width=True):
                    st.session_state.mt_overlays = []
                    st.rerun()
            else:
                st.info("No overlays added yet. Use the 'Add' form on the left.")

        # --- Step 4: Finishing ---
        st.divider()
        st.subheader("Step 4: Final Processing")
        if st.button("🚀 Process Final Video", type="primary", use_container_width=True):
            st.write("🎬 **Building final clip... This may take a moment.**")
            final_clip = video
            
            # 1. Audio Processing
            if audio:
                v_audio = video.audio.volumex(v_vol) if video.audio else None
                # Trim and offset the music clip
                m_audio = audio.subclip(a_start, a_end).volumex(a_vol).set_start(v_start)
                final_clip = video.set_audio(CompositeAudioClip([v_audio, m_audio]) if v_audio else m_audio)
            
            # 2. Text Overlays
            text_clips = []
            if st.session_state.mt_overlays:
                f_path = fonts[sel_font] if fonts else None
                final_clip, text_clips = apply_text_overlays(final_clip, st.session_state.mt_overlays, f_path)
            
            # 3. Write output
            out_name = os.path.join("temp_outputs", f"Final_Edit_{datetime.now().strftime('%H%M%S')}.mp4")
            final_clip.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(final_clip.fps*final_clip.duration)))
            
            st.success("🎉 **Success! Final edit complete.**")
            with st.container(border=True):
                res_col1, res_col2 = st.columns([0.7, 0.3])
                with res_col1:
                    with st.expander("👁️ Preview Result", expanded=True):
                        st.video(out_name)
                with res_col2:
                    st.markdown("#### 📥 Actions")
                    with open(out_name, "rb") as f:
                        st.download_button("Download Final", f, file_name=os.path.basename(out_name), use_container_width=True, type="primary")
                    if st.button("🗑️ Clear Result", key="clear_final"):
                        uf.remove_temp_files(out_name)
                        st.rerun()
            
            uf.close_and_remove(final_clip, *text_clips)
            if audio: audio.close()
            video.close()

# --- 📜 Batch Subtitles Tab ---
with tab_batch:
    st.header("📜 Batch Subtitle Overlay")
    st.info("""
    Upload a CSV or XLSX file to add many text overlays at once. 
    Required columns: **text**, **start**, **end** (in seconds).
    """)
    
    with st.expander("📝 View File Template Guide"):
        st.markdown("""
        Your file should look like this:
        | text | start | end |
        | :--- | :--- | :--- |
        | Hello World | 0.5 | 3.0 |
        | Welcome to the video | 4.2 | 7.5 |
        """)
        # Mock download button for template
        template_csv = "text,start,end\nHello World,0.5,3.0\nWelcome to the video,4.2,7.5"
        st.download_button("📥 Download CSV Template", template_csv, "subtitle_template.csv", "text/csv")

    st.divider()
    st.subheader("Step 1: Upload Files")
    col1, col2 = st.columns(2)
    bv_file = col1.file_uploader("Upload Video", type=["mp4","mov","avi"], key=f"batch_v_{st.session_state.reset_key}")
    bs_file = col2.file_uploader("Upload Subtitles (CSV/XLSX)", type=["csv", "xlsx"], key=f"batch_s_{st.session_state.reset_key}")
    
    if bv_file and bs_file:
        bv_path = uf.save_temp_file(bv_file, ".mp4")
        b_video = VideoFileClip(bv_path)
        
        # Split view for data/metrics and preview
        b_col1, b_col2 = st.columns([0.7, 0.3])
        
        with b_col1:
            st.metric("Video Duration", f"{b_video.duration:.2f}s")
            # Load subtitles
            df = pd.read_csv(bs_file) if bs_file.name.endswith(".csv") else pd.read_excel(bs_file)
            st.subheader("Step 2: Preview & Edit Data")
            edited_df = st.data_editor(df, use_container_width=True)
            
        with b_col2:
            st.subheader("📺 Source Video")
            st.video(bv_file)
        
        required = ["text", "start", "end"]
        if all(c in edited_df.columns for c in required):
            st.divider()
            st.subheader("Step 3: Global Style & Process")
            
            p_col1, p_col2 = st.columns(2)
            fonts = get_fonts()
            b_font = p_col1.selectbox("Font Family", list(fonts.keys()) if fonts else ["Arial"], key="b_f")
            b_size = p_col2.number_input("Global Font Size", 10, 200, 25, key="b_s")
            
            p_col1, p_col2 = st.columns(2)
            b_pos = p_col1.selectbox("Overlay Position", ["Bottom center", "Top center", "Center", "Top-left", "Top-right", "Bottom-left", "Bottom-right", "Custom (percent)"], key="b_p")
            b_pad = p_col2.number_input("Global Padding (px)", 0, 100, 15, key="b_pd")
            
            bx_pct, by_pct = 50, 90
            if b_pos == "Custom (percent)":
                bpx1, bpx2 = st.columns(2)
                bx_pct = bpx1.slider("Horizontal %", 0, 100, 50, key="batch_x")
                by_pct = bpx2.slider("Vertical %", 0, 100, 90, key="batch_y")
            
            if st.button("🚀 Process Batch Video", type="primary", use_container_width=True):
                st.write("🎬 **Processing batch subtitles... Please wait.**")
                batch_overlays = []
                for _, row in edited_df.iterrows():
                    batch_overlays.append({
                        "text": str(row["text"]), "start": float(row["start"]), "end": float(row["end"]),
                        "font_size": b_size, "color": "#FFFFFF", "bg_color": (0,0,0),
                        "bg_opacity": 0.7, "padding": b_pad, "position": b_pos,
                        "x_percent": bx_pct, "y_percent": by_pct
                    })
                
                font_p = fonts[b_font] if fonts else None
                final_b, b_text_clips = apply_text_overlays(b_video, batch_overlays, font_p)
                
                out_name = os.path.join("temp_outputs", f"Batch_Subtitles_{datetime.now().strftime('%H%M%S')}.mp4")
                final_b.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(final_b.fps*final_b.duration)))
                
                st.success("🎉 **Success! Batch processing done.**")
                with st.container(border=True):
                    res_col1, res_col2 = st.columns([0.7, 0.3])
                    with res_col1:
                        with st.expander("👁️ Preview Result", expanded=True):
                            st.video(out_name)
                    with res_col2:
                        st.markdown("#### 📥 Actions")
                        with open(out_name, "rb") as f:
                            st.download_button("Download Batch", f, file_name=os.path.basename(out_name), use_container_width=True, type="primary")
                        if st.button("🗑️ Clear Result", key="clear_batch"):
                            uf.remove_temp_files(out_name)
                            st.rerun()
                
                uf.close_and_remove(final_b, *b_text_clips)
                b_video.close()
        else:
            st.error(f"Missing required columns. Please ensure your file has: {required}")

# Footer
st.markdown("---")
st.caption("Mega Video Editor - Powered by MoviePy & Streamlit")
