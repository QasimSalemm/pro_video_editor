[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://videoseditor.streamlit.app/)

# Streamlit Video Editor - All-in-One Studio

🔗 https://videoseditor.streamlit.app/



A powerful, web-based video editing suite built with **Streamlit**, **MoviePy**, and **PySide6**. This application provides a user-friendly interface for common video editing tasks, offering professional-grade features like precise trimming, merging, and high-quality subtitle overlays.

---

## Features

### Trim & Subclip
- **Millisecond Precision**: Cut your videos exactly where you want.
- **Live Preview**: Preview your segments before rendering.
- **Fast Processing**: Optimized for quick exports using configurable threading.

### Video Merging
- **Flexible Strategies**: 
  - `Compose`: Handles videos with different resolutions and aspect ratios.
  - `Chain`: Ultra-fast merging for videos with identical properties.
- **Bulk Upload**: Merge multiple clips into a single masterpiece in one go.

### Music & Text Overlays
- **Audio Integration**: Add background music to your videos with ease.
- **Advanced Text Rendering**: Powered by **PySide6 (Qt)** for superior font anti-aliasing, rounded background boxes, and precise positioning.
- **Custom Fonts**: Support for various font families (Arial, Tahoma, Verdana, etc.) and custom `.ttf` files.
- **Bulk Subtitles**: Upload a CSV or XLSX file to automatically generate and overlay hundreds of subtitles.

### Pro Rendering Engine
- **Codec Control**: Support for `libx264`, `mpeg4`, and `libvpx`.
- **Audio Optimization**: Choose between `aac`, `mp3`, and `libvorbis`.
- **Performance Tuning**: Adjust encoding speed (from `ultrafast` to `slow`) and CPU threading to match your hardware.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/QasimSalemm/pro_video_editor.git
cd video-editor
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. FFmpeg Requirement
Ensure you have FFmpeg installed on your system. `imageio` will typically handle this, but for some systems, you might need to install it manually:
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: [Download from FFmpeg.org](https://ffmpeg.org/download.html)

---

## Usage

1. **Start the Application**:
   ```bash
   streamlit run Home.py
   ```
2. **Navigate the Sidebar**: Choose between the different tools (Trim, Merge, Music & Text).
3. **Configure Settings**: Use the "Global Settings" in the sidebar to adjust codecs and rendering speed.
4. **Maintenance**: Use the "Reset Project" button to clear your workspace and temporary files.

---

## Project Structure

- `Home.py`: Main entry point and navigation logic.
- `tabs/`: Modularized UI components for different editing features.
- `qt_renderer.py`: Offscreen Qt-based engine for high-quality text rendering.
- `utility_functions.py`: Workspace management and helper utilities.
- `fonts/`: Directory for custom `.ttf` font files.
- `temp_uploads/` & `temp_outputs/`: Temporary directories for file processing (auto-cleaned).

---

## Privacy & Maintenance
- **Local Processing**: All video processing occurs in local temporary folders.
- **Auto-Cleanup**: The system automatically deletes temporary files older than 2 hours to save disk space.
- **Manual Reset**: Clear all uploads and outputs instantly via the "Reset Project" button.

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed by **Qasim Saleem***
