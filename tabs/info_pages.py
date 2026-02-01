import streamlit as st

def render_contact():
    st.title("Contact Us")
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
        st.write("qasimsaleem317@gmail.com")
    with col2:
        st.subheader("Response Time")
        st.write("We typically respond within 24-48 hours.")
    


def render_privacy_policy():
    st.title("Privacy Policy")
    st.write("Last Updated: January 1, 2026")

    st.header("1. Data Collection")
    st.write("We collect minimal data necessary to provide our video editing services. This includes the video and audio files you upload for processing.")

    st.header("2. File Processing")
    st.write("Your files are processed on our servers to perform the requested edits. Temporary files created during processing are automatically deleted after a short period.")

    st.header("3. Data Security")
    st.write("We implement security measures to protect your files while they are on our servers. We do not share your uploaded content with third parties.")

    st.header("4. Cookies")
    st.write("We use essential cookies to maintain your session and ensure the application functions correctly.")

    st.header("5. Changes to This Policy")
    st.write("We may update this privacy policy from time to time. We will notify users of any significant changes.")



def render_terms_conditions():
    st.title("Terms & Conditions")
    st.write("Last Updated: January 1, 2026")

    st.header("1. Acceptance of Terms")
    st.write("By using the Video Editor, you agree to comply with and be bound by these terms and conditions.")

    st.header("2. User Conduct")
    st.write("Users must not use the platform for any illegal or unauthorized purpose. You are solely responsible for the content you upload and process.")

    st.header("3. Intellectual Property")
    st.write("Video Editor does not claim ownership of the content you upload. However, you represent that you have the necessary rights to use and edit such content.")

    st.header("4. Limitation of Liability")
    st.write("We provide this service 'as is' without any warranties. We are not liable for any damages resulting from the use or inability to use our platform.")

    st.header("5. Termination")
    st.write("We reserve the right to terminate or restrict access to the service at our sole discretion, without notice.")



def render_guide_video_tools():
    st.title("Guide: Video Tools")

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

def render_guide_subtitles():
    st.title("Guide: Text & Subtitles")

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
    

