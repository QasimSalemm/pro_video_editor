import os
import json
import subprocess
import tempfile
import sys

def create_text_overlay_image(
    text,
    font_path=None,
    font_family="Arial",
    font_size=40,
    text_color=(255, 255, 255),
    bg_color=None,          # RGB tuple
    bg_opacity=0.5,         # 0.0 to 1.0
    padding=20,
    corner_radius=7.5
):
    """
    Calls the external qt_renderer.py script to generate the image.
    This avoids threading crashes when running PySide6 inside Streamlit.
    """
    
    # Create a temp file path for the output image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    out_path = temp_file.name
    temp_file.close()

    # Prepare arguments
    args = {
        "text": text,
        "font_path": font_path,
        "font_family": font_family,
        "font_size": font_size,
        "text_color": text_color,
        "bg_color": bg_color,
        "bg_opacity": bg_opacity,
        "padding": padding,
        "corner_radius": corner_radius,
        "out_path": out_path
    }

    renderer_script = os.path.join(os.path.dirname(__file__), "qt_renderer.py")
    
    try:
        # Run the renderer in a separate process
        process = subprocess.run(
            [sys.executable, renderer_script, "--json", json.dumps(args)],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "SUCCESS" in process.stdout:
            return out_path
        else:
            print(f"Renderer Error Output: {process.stderr}")
            print(f"Renderer Standard Output: {process.stdout}")
            raise RuntimeError("Renderer script failed to generate image.")

    except subprocess.CalledProcessError as e:
        print(f"Subprocess Error: {e.stderr}")
        raise RuntimeError(f"Failed to execute Qt renderer: {e.stderr}")
