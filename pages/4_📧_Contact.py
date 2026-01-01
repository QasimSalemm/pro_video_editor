import streamlit as st

st.set_page_config(
    page_title="Contact Us - Mega Video Editor",
    page_icon="📧"
)

st.title("📧 Contact Us")

st.write("Have questions, feedback, or need support? We're here to help.")

with st.form("contact_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    subject = st.selectbox("Subject", ["Support", "Feedback", "Business Inquiry", "Other"])
    message = st.text_area("Message")
    
    submit_button = st.form_submit_button("Send Message")
    
    if submit_button:
        if name and email and message:
            st.success(f"Thank you {name}, your message has been sent successfully!")
        else:
            st.error("Please fill in all required fields.")

st.header("Other Ways to Reach Us")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Support Email")
    st.write("support@megavideoeditor.com")
with col2:
    st.subheader("Response Time")
    st.write("We typically respond within 24-48 hours.")

st.divider()
st.caption("© 2026 Mega Video Editor. All rights reserved.")
