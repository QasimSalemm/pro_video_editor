import streamlit as st

st.set_page_config(
    page_title="Privacy Policy - Mega Video Editor",
    page_icon="🛡️"
)

st.title("🛡️ Privacy Policy")

st.write("Last Updated: January 1, 2026")

st.header("1. Data Collection")
st.write(
    "We collect minimal data necessary to provide our video editing services. "
    "This includes the video and audio files you upload for processing."
)

st.header("2. File Processing")
st.write(
    "Your files are processed on our servers to perform the requested edits. "
    "Temporary files created during processing are automatically deleted after a short period."
)

st.header("3. Data Security")
st.write(
    "We implement security measures to protect your files while they are on our servers. "
    "We do not share your uploaded content with third parties."
)

st.header("4. Cookies")
st.write(
    "We use essential cookies to maintain your session and ensure the application functions correctly."
)

st.header("5. Changes to This Policy")
st.write(
    "We may update this privacy policy from time to time. We will notify users of any significant changes."
)

st.divider()
st.caption("© 2026 Mega Video Editor. All rights reserved.")
