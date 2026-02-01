import os
import streamlit as st
import utility_functions as uf
import streamlit_logger as sl
from datetime import datetime
from moviepy.editor import VideoFileClip
import ui_components as ui

def render_trim_tab(codec, audio_codec, render_preset, render_threads):
    with st.container():
        video_file = st.file_uploader("Upload Video", type=["mp4","mov","avi"], key=f"trim_{st.session_state.reset_key}")
    
    if video_file:
        video_path = uf.save_temp_file(video_file, ".mp4")
        video = VideoFileClip(video_path)
        
        # 1. Full-Width Info
        with st.expander("Uploaded Video Info", expanded=False):
            st.write(f"**Name:** {video_file.name}")
            st.write(f"**Format:** `{video.w}x{video.h}`")
            st.write(f"**Duration:** `{video.duration:.2f}s` | **FPS:** `{video.fps}`")

        # 2. Side-by-Side Focus: Settings (Left) & Monitor (Right)
        col_settings, col_monitor = st.columns([0.45, 0.55])
        
        with col_settings:
            st.markdown("### Settings")
            with st.expander("Trim Settings", expanded=True):
                start = st.number_input("Start (s)", 0.0, video.duration, 0.0, step=0.1, key="t_start")
                end = st.number_input("End (s)", 0.0, video.duration, min(5.0, video.duration), step=0.1, key="t_end")
                sel_len = max(0.0, end - start)
                st.metric("New Duration", f"{sel_len:.2f}s")
            
            # Preview Controls moved to Left Column
            st.markdown("### Preview Controls")
            w_pct, h_px = ui.render_preview_controls("trim_m_w", "trim_m_h", expanded=True)

        with col_monitor:
            # Video Display in Right Column
            ui.render_preview_video(video_file, w_pct, h_px, caption_text=f"Editing: {video_file.name}")
                
        # --- Full-Width Action Row ---
        if st.button("Create Subclip", type="primary", use_container_width=True):
            if start < end:
                st.write("**Creating Subclip...**")
                sub = video.subclip(start, end)
                out_name = os.path.join("temp_outputs", f"Trimmed_{datetime.now().strftime('%H%M%S')}.mp4")
                sub.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(sub.fps*sub.duration)))
                
                st.session_state.trim_final_out_path = out_name
                st.success("✨ **Success!**")
                
                sub.close()
                video.close()
                st.rerun()
            else:
                st.warning("Start time must be less than end time.")

        # --- Master Presentation ---
        if st.session_state.trim_final_out_path:
            def reset_trim():
                st.session_state.trim_final_out_path = None
            
            ui.render_final_presentation(
                st.session_state.trim_final_out_path,
                "trim_pres_w", "trim_pres_h",
                "Download Trimmed Video",
                reset_trim
            )
        
        video.close()
