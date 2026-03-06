import os
import streamlit as st
import utility_functions as uf
import streamlit_logger as sl
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
import ui_components as ui

def render_merge_tab(codec, audio_codec, render_preset, render_threads, merge_method): 
    with st.container():
        files = st.file_uploader("Select Multiple Clips", type=["mp4","mov","avi"], accept_multiple_files=True, key=f"merge_{st.session_state.reset_key}")    
    if files:
        # --- Parallel Sequence & Settings ---
        col_seq, col_set = st.columns([0.7, 0.3])
        
        with col_seq:
            with st.expander("Clip Sequence", expanded=False):
                clips = []
                for i, f in enumerate(files):
                    p = uf.save_temp_file(f, ".mp4")
                    c = VideoFileClip(p)
                    clips.append(c)
                    st.markdown(f"**{i+1}.** {f.name} — `{c.duration:.2f}s` (`{c.w}x{c.h}`)")

        with col_set:
            with st.expander("Merge Settings", expanded=False):
                st.info(f"**Total:** `{len(clips)}` clips  \n**Final:** `{sum(c.duration for c in clips):.2f}s`  \n**Method:** `{merge_method}`")
        
        # --- Full-Width Action Row ---
        if st.button("Merge Clips", type="primary", width="stretch"):
            if len(clips) >= 2:
                st.write("**Merging...**")
                final = concatenate_videoclips(clips, method=merge_method)
                out_name = os.path.join("temp_outputs", f"Merged_{datetime.now().strftime('%H%M%S')}.mp4")
                final.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(final.fps*final.duration)))
                
                st.session_state.merge_final_out_path = out_name
                st.success("✨ **Success!**")
                
                uf.close_and_remove(final, *clips)
                st.rerun()
            else:
                st.warning("Needs 2+ clips to merge.")

        # --- Master Presentation ---
        if st.session_state.merge_final_out_path:
            def reset_merge():
                st.session_state.merge_final_out_path = None

            ui.render_final_presentation(
                st.session_state.merge_final_out_path,
                "merge_pres_w", "merge_pres_h",
                "Download Merged Video",
                reset_merge
            )
