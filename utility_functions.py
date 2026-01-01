import os
import shutil
from random import randint
import tempfile
from datetime import datetime

# ==============================
# Utility Functions
# ==============================
def seconds_to_hms(seconds: int):
    """Convert seconds → (h, m, s)."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return h, m, s

def hms_to_seconds(h: int, m: int, s: int):
    """Convert (h, m, s) → seconds."""
    return int(h) * 3600 + int(m) * 60 + int(s)

def save_temp_file(uploaded_file, suffix=".mp4", folder="temp_uploads"):
    """Save an uploaded file to a specific folder and return the path."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Use a unique name to avoid collisions
    temp_name = f"tmp_{randint(0, 100000)}_{datetime.now().strftime('%H%M%S')}{suffix}"
    path = os.path.join(folder, temp_name)
    
    with open(path, "wb") as f:
        f.write(uploaded_file.read())
    return path

def cleanup_workspace(directories=["temp_uploads", "temp_outputs"]):
    """Performs a full purge of the specified directories."""
    for directory in directories:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

def init_workspace(directories=["temp_uploads", "temp_outputs"]):
    """Ensures workspace directories exist."""
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def close_and_remove(*clips):
    for clip in clips:
        try:
            clip.close()
        except Exception:
            pass

def remove_temp_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

def generate_key(prefix):
    return f"{prefix}_{randint(0, 100000)}"