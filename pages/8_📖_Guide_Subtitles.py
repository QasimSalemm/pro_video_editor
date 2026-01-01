import streamlit as st

st.set_page_config(
    page_title="How to Use Subtitles - Mega Video Editor",
    page_icon="📖"
)

st.title("📖 Guide: Text & Subtitles")

st.header("1. Manual Text Overlays")
st.write("1. **Upload Sources**: Upload your video in the **Music & Text** tab.")
st.write("2. **Configure Mix**: Adjust volumes in Step 2.")
st.write("3. **Add Text**: Use the 'Add New Overlay' form in Step 3. You can customize font, size, and background.")
st.write("4. **Manage List**: Review and delete overlays in the 'Current Overlays List'.")
st.write("5. **Process**: Click **Process Final Video** in Step 4.")

st.header("2. Batch Subtitles (Excel/CSV)")
st.write("1. **Upload**: In the **Batch Subtitles** tab, upload your video and a CSV/XLSX file.")
st.write("2. **Columns**: Your file must have **text**, **start**, and **end** columns.")
st.write("3. **Edit Live**: Use the interactive table to fix any typos or timing issues on the fly.")
st.write("4. **Global Style**: Choose one look for all subtitles and click **Process Batch Video**.")

st.header("3. Custom Positioning")
st.write("Use the **Custom (percent)** option to place text anywhere on the screen using the X and Y sliders.")

st.divider()
st.warning("⚠️ Make sure your subtitle timings do not exceed the video duration.")

# Footer
st.caption("© 2026 Mega Video Editor. All rights reserved.")
