import streamlit as st

st.set_page_config(
    page_title="How to Use Video Tools - Mega Video Editor",
    page_icon="📖"
)

st.title("📖 Guide: Video Tools")

st.header("1. Trimming Videos")
st.write("To trim a video and create a subclip:")
st.write("1. **Upload**: Choose your video in the **Trim & Subclip** tab.")
st.write("2. **Ranges**: Use the 'Select Range' inputs to set start/end times.")
st.write("3. **Preview**: Verify your selection in the live preview window.")
st.write("4. **Render**: Click **Generate Subclip**. Track the progress bar for frame-by-frame updates.")

st.header("2. Merging Videos")
st.write("To concatenate multiple videos into one:")
st.write("1. Upload two or more video files in the **Merge Videos** tab.")
st.write("2. They will be processed in the order they were uploaded.")
st.write("3. Click **Merge All Now**.")
st.write("4. Download the resulting concatenated video.")

st.header("3. Adding Music")
st.write("To add background music:")
st.write("1. Go to the **Music & Text** tab.")
st.write("2. Upload your main video and an audio file.")
st.write("3. Adjust the volume sliders for both tracks.")
st.write("4. Click **Process Final Video**.")

st.divider()
st.info("💡 For best results, use high-quality source files and standard formats like MP4 and MP3.")

# Footer
st.caption("© 2026 Mega Video Editor. All rights reserved.")
