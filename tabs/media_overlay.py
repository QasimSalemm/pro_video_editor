import os
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, afx
import utility_functions as uf
import image_generator as ig
import position_helpers as ph
import streamlit_logger as sl
import ui_components as ui
from datetime import datetime

# --- Helper Functions Specific to this Tab ---

def load_layer_to_sidebar(index, layer_data):
    st.session_state.mt_edit_index = index
    st.session_state.mt_txt_input = layer_data['text']
    st.session_state.mt_s_t = layer_data['start']
    st.session_state.mt_e_t = layer_data['end']
    st.session_state.mt_f_size = layer_data['font_size']
    st.session_state.mt_f_fam = layer_data.get('font_fam', 'Arial')
    st.session_state.mt_t_col = layer_data['color']
    st.session_state.mt_b_col = '#{:02x}{:02x}{:02x}'.format(*layer_data['bg_color'])
    st.session_state.mt_b_opac = layer_data.get('bg_opacity', 0.7)
    st.session_state.mt_pad = layer_data.get('padding', 15)
    st.session_state.mt_pos = layer_data['position']
    st.session_state.mt_x_pct = layer_data.get('x_percent', 50)
    st.session_state.mt_y_pct = layer_data.get('y_percent', 90)

def load_bulk_row_to_preview():
    if "mt_bulk_df" in st.session_state and st.session_state.mt_bulk_df is not None:
        idx = st.session_state.get("mt_bulk_row_num", 0)
        df = st.session_state.mt_bulk_df
        if 0 <= idx < len(df):
            row = df.iloc[idx]
            # Handle case-insensitive columns
            cols = {c.lower(): c for c in df.columns}
            
            if "text" in cols:
                st.session_state.mt_txt_input = str(row[cols["text"]])
            
            try:
                s_col = cols.get("start")
                e_col = cols.get("end")
                s_t = float(row[s_col]) if s_col else 0.0
                e_t = float(row[e_col]) if e_col else 5.0
                
                st.session_state.mt_s_t = s_t if not (np.isnan(s_t) or np.isinf(s_t)) else 0.0
                st.session_state.mt_e_t = e_t if not (np.isnan(e_t) or np.isinf(e_t)) else 5.0
                st.toast(f"✅ Loaded Row {idx+1} into monitor!")
            except Exception as e:
                st.error(f"Error loading timings: {e}")
                st.session_state.mt_s_t = 0.0
                st.session_state.mt_e_t = 5.0

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

def render_media_overlay_tab(codec, audio_codec, render_preset, render_threads):
    # --- Step 1: Sources (Prominent) ---
    with st.container():
        v_file = st.file_uploader("Upload Base Video to Start", type=["mp4","mov","avi"], key=f"mt_v_{st.session_state.reset_key}")
    
    if v_file:
        v_path = uf.save_temp_file(v_file, ".mp4")
        video = VideoFileClip(v_path)
        
        st.markdown("### Studio Tools")
        
        # 1. Horizontal Mode Switch (Top Bar)
        edit_mode = st.radio("Select Tool:", ["Text Overlays", "Music & Audio"], horizontal=True, label_visibility="collapsed", key="mt_edit_mode")

        # --- Parallel Layout: Settings (Left) & Monitor (Right) ---
        col_settings, col_monitor = st.columns([0.45, 0.55])
        
        with col_settings:
            st.markdown("### Settings")
            if edit_mode == "Music & Audio":
                with st.expander("Audio Settings", expanded=True):
                    a_file = st.file_uploader("Upload Audio Source", type=["mp3","wav"], key=f"mt_a_{st.session_state.reset_key}")
                    if a_file:
                        a_path = uf.save_temp_file(a_file, ".mp3")
                        audio = AudioFileClip(a_path)
                        st.markdown("**Mixing**")
                        v_vol = st.slider("Video Volume", 0.0, 1.0, 1.0, 0.05, key="mt_v_vol")
                        a_vol = st.slider("Music Volume", 0.0, 1.0, 0.5, 0.05, key="mt_a_vol")
                        st.markdown("**Precision Timing**")
                        a_s = st.number_input("Music Start (s)", 0.0, audio.duration, 0.0, step=0.1, key="mt_a_s")
                        a_e = st.number_input("Music End (s)", 0.0, audio.duration, audio.duration, step=0.1, key="mt_a_e")
                        v_s = st.number_input("Start on Video at (s)", 0.0, video.duration, 0.0, step=0.1, key="mt_v_s")
                        st.session_state.audio_settings = {"v_vol": v_vol, "a_vol": a_vol, "a_start": a_s, "a_end": a_e, "v_start": v_s, "audio_clip": audio}
                    else:
                        st.info("Upload an audio file to start mixing.")
                
                # Symmetrical Monitor Controls for Audio Mode
                with st.expander("Preview Monitor", expanded=False):
                    st.slider("Scale Width (%)", 10, 100, 50, step=5, key="mt_m_w_audio")
                    st.number_input("Fixed Height (px) [0=Auto]", 0, 2000, 0, step=50, key="mt_m_h_audio")
                    st.caption("💡 Use '0' height to maintain aspect ratio based on width.")

            else:
                # 1. Text Content (Expanded by default)
                with st.expander("Text Content", expanded=True):
                    txt = st.text_area("Overlay Text", placeholder="What should it say?", key="mt_txt_input")
                    t1, t2 = st.columns(2)
                    s_t = t1.number_input("Start (s)", 0.0, video.duration, step=0.5, key="mt_s_t")
                    e_t = t2.number_input("End (s)", 0.0, video.duration, step=0.5, key="mt_e_t")
                    
                    is_editing = st.session_state.mt_edit_index is not None
                    btn_label = "Update Layer" if is_editing else "Add Layer to Project"
                    
                    if st.button(btn_label, use_container_width=True, type="primary"):
                        if txt.strip():
                            # Style widgets are defined below, but their keys are accessible in session state
                            fonts = ui.get_fonts()
                            sel_f = st.session_state.get("mt_f_fam", "Arial")
                            f_sz = st.session_state.get("mt_f_size", 20)
                            pos = st.session_state.get("mt_pos", "Bottom center")
                            x_pct = st.session_state.get("mt_x_pct", 50)
                            y_pct = st.session_state.get("mt_y_pct", 90)
                            t_c = st.session_state.get("mt_t_col", "#000000")
                            b_c = st.session_state.get("mt_b_col", "#FFFEFF")
                            b_op = st.session_state.get("mt_b_opac", 0.50)
                            pad = st.session_state.get("mt_pad", 10)

                            new_layer = {
                                "text": txt, "start": s_t, "end": e_t, "font_size": f_sz,
                                "color": t_c, "bg_color": tuple(int(b_c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)),
                                "bg_opacity": b_op, "padding": pad, "position": pos,
                                "x_percent": x_pct, "y_percent": y_pct,
                                "font_fam": sel_f
                            }
                            
                            if is_editing:
                                st.session_state.mt_overlays[st.session_state.mt_edit_index] = new_layer
                                st.session_state.mt_edit_index = None
                                st.success("Layer updated!")
                            else:
                                st.session_state.mt_overlays.append(new_layer)
                            st.rerun()
                    
                    if is_editing:
                        if st.button("Cancel Edit", use_container_width=True):
                            st.session_state.mt_edit_index = None
                            st.rerun()

                # 2. Bulk Import
                with st.expander("Bulk Import (CSV/XLSX)", expanded=False):
                    st.caption("Upload a file with 'text', 'start', and 'end' columns. You can edit the data below before importing.")
                    bulk_file = st.file_uploader("Select Spreadsheet", type=["csv", "xlsx"], key="mt_bulk_up")
                    if bulk_file:
                        try:
                            if st.session_state.mt_bulk_df is None or st.session_state.get("last_uploaded") != bulk_file.name:
                                chunk = pd.read_csv(bulk_file) if bulk_file.name.endswith(".csv") else pd.read_excel(bulk_file)
                                # Standardize column names for processing
                                chunk.columns = [str(c).strip().lower() for c in chunk.columns]
                                st.session_state.mt_bulk_df = chunk
                                st.session_state.last_uploaded = bulk_file.name
                            
                            df = st.data_editor(st.session_state.mt_bulk_df, use_container_width=True, key="mt_bulk_editor")
                            st.session_state.mt_bulk_df = df # Keep edits in state
                            
                            required = ["text", "start", "end"]
                            if all(item in df.columns for item in required):
                                st.divider()
                                # Row Selection
                                st.number_input("Preview Row #", 0, len(df)-1, 0, key="mt_bulk_row_num")
                                
                                # Actions stacked vertically
                                st.button("👁️ Load into Monitor", use_container_width=True, on_click=load_bulk_row_to_preview)
                                
                                if st.button("➕ Import All as Layers", use_container_width=True, type="primary"):
                                    # Get current styles
                                    cur_f_sz = st.session_state.get("mt_f_size", 20)
                                    cur_t_c = st.session_state.get("mt_t_col", "#000000")
                                    cur_b_c = st.session_state.get("mt_b_col", "#FFFEFF")
                                    cur_b_op = st.session_state.get("mt_b_opac", 0.50)
                                    cur_pad = st.session_state.get("mt_pad", 10)
                                    cur_pos = st.session_state.get("mt_pos", "Bottom center")
                                    cur_x = st.session_state.get("mt_x_pct", 50)
                                    cur_y = st.session_state.get("mt_y_pct", 90)

                                    for _, row in df.iterrows():
                                        st.session_state.mt_overlays.append({
                                            "text": str(row["text"]), "start": float(row["start"]), "end": float(row["end"]),
                                            "font_size": cur_f_sz, "color": cur_t_c,
                                            "bg_color": tuple(int(cur_b_c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)),
                                            "bg_opacity": cur_b_op, "padding": cur_pad, "position": cur_pos,
                                            "x_percent": cur_x, "y_percent": cur_y 
                                        })
                                    st.success(f"Imported {len(df)} layers!")
                                    st.rerun()

                            else:
                                st.error(f"Missing columns. Need: {required}")
                        except Exception as e:
                            st.error(f"Error processing file: {e}")

                # 3. Appearance & Position
                with st.expander("Appearance & Position", expanded=False):
                    f1, f2 = st.columns(2)
                    fonts = ui.get_fonts()
                    f1.selectbox("Font", list(fonts.keys()) if fonts else ["Arial"], key="mt_f_fam")
                    f2.number_input("Size", 10, 200, value=20, step=1, key="mt_f_size")
                    
                    pos_val = st.selectbox("Position", ["Bottom center", "Top center", "Center", "Top-left", "Top-right", "Bottom-left", "Bottom-right", "Custom (percent)"], key="mt_pos")
                    
                    if pos_val == "Custom (percent)":
                        p1, p2 = st.columns(2)
                        p1.slider("X%", 0, 100, value=50, key="mt_x_pct")
                        p2.slider("Y%", 0, 100, value=90, key="mt_y_pct")
                        
                    c1, c2 = st.columns(2)
                    c1.color_picker("Text Color", "#000000", key="mt_t_col")
                    c2.color_picker("Background", "#FFFEFF", key="mt_b_col")
                    st.slider("BG Opacity", 0.0, 1.0, value=0.50, step=0.05, key="mt_b_opac")
                    st.number_input("Global Padding", 0, 100, value=10, step=1, key="mt_pad")

                # 4. Monitor Controls   
                with st.expander("Preview Monitor Controls", expanded=False):
                    st.slider("Scale Width (%)", 10, 100, 50, step=5, key="mt_m_w")
                    st.number_input("Fixed Height (px) [0=Auto]", 0, 2000, 0, step=50, key="mt_m_h")
                    st.caption("💡 Use '0' height to maintain aspect ratio based on width.")

        with col_monitor:
            # Get Monitor Settings - Handle both mode keys
            if edit_mode == "Music & Audio":
                final_w_pct = st.session_state.get("mt_m_w_audio", 50)
                final_h_val = st.session_state.get("mt_m_h_audio", 0)
            else:
                final_w_pct = st.session_state.get("mt_m_w", 50)
                final_h_val = st.session_state.get("mt_m_h", 0)
            
            # Calculate margins for centering all monitor elements
            margin = (100 - final_w_pct) / 200.0
            if margin > 0:
                m_left, m_mid, m_right = st.columns([margin, final_w_pct/100.0, margin])
            else:
                m_mid = st.container()

            with m_mid:
                st.markdown("<h3 style='text-align: center;'>Preview Monitor</h3>", unsafe_allow_html=True)
                if edit_mode == "Music & Audio":
                    st.video(v_file)
                    # Audio Preview
                    # a_file is defined in the settings column scope above. 
                    # We might need to access it from session state or just check local var if python scoping permits (it does).
                    # However, to be safe and robust, let's verify if 'a_file' is bound.
                    if 'a_file' in locals() and a_file:
                        st.markdown("---")
                        st.caption("Audio Preview")
                        st.audio(a_file)
                else:
                    # Text Mode - Master Preview (Live Edit + All Active Layers)
                    try:
                        # 1. Get current state
                        live_txt = st.session_state.get("mt_txt_input", "").strip()
                        current_t = st.session_state.get("mt_s_t", 0.0)
                        
                        # 2. Get the base frame
                        clamped_t = max(0.0, min(current_t, video.duration - 0.01))
                        frame = video.get_frame(clamped_t)
                        combined = Image.fromarray(frame).convert("RGBA")
                        
                        fonts = ui.get_fonts()
                        
                        # 3. Collect all overlays to render (Timeline + Live)
                        to_render = []
                        
                        # Add timeline layers that are active at this time
                        for o in st.session_state.get("mt_overlays", []):
                            if o["start"] <= clamped_t <= o["end"]:
                                to_render.append(o)
                        
                        # Add the live-edit layer on top if it has text
                        if live_txt:
                            f_fam = st.session_state.get("mt_f_fam", "Arial")
                            f_path = fonts[f_fam] if fonts and f_fam in fonts else None
                            b_c = st.session_state.get("mt_b_col", "#000000")
                            to_render.append({
                                "text": live_txt,
                                "font_size": st.session_state.get("mt_f_size", 20),
                                "color": st.session_state.get("mt_t_col", "#000000"),
                                "bg_color": tuple(int(b_c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)),
                                "bg_opacity": st.session_state.get("mt_b_opac", 0.50),
                                "padding": st.session_state.get("mt_pad", 10),
                                "position": st.session_state.get("mt_pos", "Bottom center"),
                                "x_percent": st.session_state.get("mt_x_pct", 50),
                                "y_percent": st.session_state.get("mt_y_pct", 90)
                            })
                        
                        # 4. Render all collected overlays
                        for ov in to_render:
                            f_fam = ov.get("font_fam", st.session_state.get("mt_f_fam", "Arial"))
                            f_path = fonts[f_fam] if fonts and f_fam in fonts else None
                            
                            ov_img_path = ig.create_text_overlay_image(
                                ov["text"], font_path=f_path, font_size=ov["font_size"],
                                text_color=tuple(int(ov["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) if isinstance(ov["color"], str) else ov["color"],
                                bg_color=ov["bg_color"], bg_opacity=ov["bg_opacity"], padding=ov["padding"]
                            )
                            ov_img = Image.open(ov_img_path).convert("RGBA")
                            
                            if ov["position"] == "Custom (percent)":
                                x_px, y_px = ph.compute_custom_xy_percent(video.w, video.h, ov_img.width, ov_img.height, ov["x_percent"], ov["y_percent"])
                            else:
                                pos_map = {"Bottom center": (0.5, 0.9), "Top center": (0.5, 0.1), "Center": (0.5, 0.5), "Top-left": (0.1, 0.1), "Top-right": (0.9, 0.1), "Bottom-left": (0.1, 0.9), "Bottom-right": (0.9, 0.9)}
                                ax, ay = pos_map.get(ov["position"], (0.5, 0.5))
                                x_px, y_px = int((video.w - ov_img.width) * ax), int((video.h - ov_img.height) * ay)

                            combined.paste(ov_img, (x_px, y_px), ov_img)
                            os.remove(ov_img_path)

                        # 5. Display result
                        disp_w = int(video.w * (final_w_pct / 100.0))
                        disp_h = final_h_val if final_h_val > 0 else int(disp_w * (video.h / video.w))
                        
                        # Save to a stable disk path to avoid Streamlit's "Bad filename" (MediaFileStorageError)
                        # We use the session_id to ensure each user/session has their own preview file
                        preview_filename = f"preview_{st.session_state.session_id}.png"
                        preview_path = os.path.join("temp_outputs", preview_filename)
                        
                        combined.resize((disp_w, disp_h)).save(preview_path)
                        
                        st.image(preview_path, use_container_width=True, caption=f"Preview Monitor at {clamped_t:.2f}s")
                        
                        if not fonts:
                            st.warning("⚠️ No system fonts found. Using basic default font.")
                            
                    except Exception as e:
                        st.error(f"Preview Error: {e}")

        # --- 📋 Global Layers Timeline (Full Width) ---
        st.divider()
        st.markdown("### Layers Timeline (Expanded View)")
        if st.session_state.mt_overlays:
            # Table-like Header for Pro Feel
            h_cols = st.columns([0.05, 0.2, 0.1, 0.1, 0.2, 0.2, 0.1])
            h_cols[0].markdown("**#**")
            h_cols[1].markdown("**Content**")
            h_cols[2].markdown("**Start (s)**")
            h_cols[3].markdown("**End (s)**")
            h_cols[4].markdown("**Position**")
            h_cols[5].markdown("**Style Details**")
            h_cols[6].markdown("**Action**")
            
            for i, o in enumerate(st.session_state.mt_overlays):
                with st.container():
                    r_cols = st.columns([0.05, 0.2, 0.1, 0.1, 0.2, 0.15, 0.2])
                    r_cols[0].write(f"{i+1}")
                    r_cols[1].write(f"{o['text'][:30]}...")
                    r_cols[2].write(f"{o['start']}")
                    r_cols[3].write(f"{o['end']}")
                    r_cols[4].write(f"{o['position']}")
                    r_cols[5].caption(f"Sz: {o['font_size']} | {o['color']}")
                    
                    b1, b2 = r_cols[6].columns(2)
                    b1.button("✏️", key=f"edit_mt_{i}", on_click=load_layer_to_sidebar, args=(i, o))
                        
                    if b2.button("🗑️", key=f"del_mt_{i}"):
                        st.session_state.mt_overlays.pop(i)
                        st.rerun()
            
            if st.button("Clear All Layers", type="secondary"):
                st.session_state.mt_overlays = []
                st.rerun()
        else:
            st.info("No layers added yet. Use the sidebar tools to create your first overlay.")

        # --- Final Export ---

        if st.button("Render & Export Final Video", type="primary", use_container_width=True):
            st.write("**Rendering your masterpiece...**")
            final_clip = video
            
            # Audio Processing
            audio_settings = st.session_state.get("audio_settings")
            if audio_settings:
                v_audio = video.audio.volumex(audio_settings["v_vol"]) if video.audio else None
                # Smart Audio Processing (Loop/Trim)
                s_clip = audio_settings["audio_clip"].subclip(audio_settings["a_start"], audio_settings["a_end"])
                
                # Calculate how long the audio needs to be to fill the rest of the video
                # If audio starts at t=0, it needs to be video.duration long.
                # If audio starts at t=5, it needs to be (video.duration - 5) long.
                needed_duration = video.duration - audio_settings["v_start"]
                
                if needed_duration > 0:
                    if s_clip.duration < needed_duration:
                        # Audio is shorter -> Loop it
                        final_audio_sub = afx.audio_loop(s_clip, duration=needed_duration)
                    else:
                        # Audio is longer -> Trim it
                        final_audio_sub = s_clip.subclip(0, needed_duration)
                    
                    m_audio = final_audio_sub.volumex(audio_settings["a_vol"]).set_start(audio_settings["v_start"])
                else:
                    m_audio = None # Audio starts after video ends

                final_clip = video.set_audio(CompositeAudioClip([v_audio, m_audio]) if v_audio and m_audio else (m_audio if m_audio else v_audio))
            
            # Text Processing
            text_clips = []
            if st.session_state.mt_overlays:
                fonts = ui.get_fonts()
                current_sel_font = st.session_state.get("mt_f_fam", "Arial")
                f_path = fonts.get(current_sel_font)
                final_clip, text_clips = apply_text_overlays(final_clip, st.session_state.mt_overlays, f_path)
            
            out_name = os.path.join("temp_outputs", f"Final_Edit_{datetime.now().strftime('%H%M%S')}.mp4")
            final_clip.write_videofile(out_name, codec=codec, audio_codec=audio_codec, preset=render_preset, threads=render_threads, logger=sl.StreamlitLogger(int(final_clip.fps*final_clip.duration)))
            
            st.session_state.mt_final_out_path = out_name
            st.success("✨ **Rendering Complete!**")
            
            uf.close_and_remove(final_clip, *text_clips)
            if audio_settings: audio_settings["audio_clip"].close()
            video.close()
            st.rerun()

        # --- Master Presentation Block (Persistent after render) ---
        if st.session_state.mt_final_out_path:
            def reset_media():
                st.session_state.mt_final_out_path = None
            
            ui.render_final_presentation(
                st.session_state.mt_final_out_path,
                "mt_pres_w", "mt_pres_h",
                "Download Master Video",
                reset_media
            )
