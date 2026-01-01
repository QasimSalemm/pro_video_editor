import streamlit as st

st.set_page_config(
    page_title="About Us - Professional Online Video Editor",
    page_icon="🎬"
)

st.title("About Us")

st.write(
    "Welcome to the **Mega Video Editor** – a professional, high-performance "
    "online tool for video manipulation. Our editor is built 100% on native "
    "Streamlit and optimized performance rendering."
)

st.header("Our Vision")
st.write(
    "We aim to empower creators, professionals, and hobbyists to edit videos "
    "efficiently without the need for complex software. Our goal is to make video editing "
    "accessible to everyone, anywhere, with just a web browser."
)

st.header("Key Features")
st.write("Our platform offers a range of powerful tools, including:")
st.write("• Merge multiple videos into one seamless video")
st.write("• Trim and create precise subclips")
st.write("• Add background music or audio tracks")
st.write("• Supports MP4, MOV, AVI, MP3, and WAV formats")
st.write("• Fast, intuitive, and completely online – no downloads required")

st.header("Why Choose Us")
st.write(
    "Our online video editor is designed for speed, simplicity, and professional quality. "
    "Whether you are a content creator, educator, or casual user, our platform allows you "
    "to create high-quality videos without installing heavy software."
)

st.header("Our Commitment")
st.write(
    "We are committed to providing a secure and reliable online platform. "
    "Your uploaded videos are processed safely, and temporary files are automatically cleaned up."
)

st.divider()
st.info("💡 This project is built using Streamlit and MoviePy for a seamless native experience.")

# Footer
st.caption("© 2026 Mega Video Editor. All rights reserved.")
