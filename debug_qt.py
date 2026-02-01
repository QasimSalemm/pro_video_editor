import os
import sys

# Set offscreen BEFORE importing Qt if possible, or right after.
os.environ["QT_QPA_PLATFORM"] = "offscreen"

try:
    from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont
    print("✅ PySide6 imported.")
except ImportError as e:
    print(f"❌ PySide6 Import Error: {e}")
    sys.exit(1)

# Init App
try:
    if not QGuiApplication.instance():
        app = QGuiApplication([])
        print("✅ QGuiApplication instantiated.")
    else:
        app = QGuiApplication.instance()
        print("✅ QGuiApplication already exists.")
except Exception as e:
    print(f"❌ QGuiApplication Success: {e}")
    sys.exit(1)

# Import our generator function
try:
    import image_generator as ig
    print("✅ image_generator imported.")
except Exception as e:
    print(f"❌ image_generator Import Error: {e}")
    # We might need to copy the function here if import fails due to other deps, 
    # but let's try importing first as it tests the file.

# Test Font Loading
font_path = os.path.join("fonts", "Noto Nastaliq Urdu Regular.ttf")
if os.path.exists(font_path):
    print(f"Font found at: {font_path}")
    try:
        font_id = QFontDatabase.addApplicationFont(font_path)
        print(f"Font ID: {font_id}")
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Loaded Families: {families}")
        else:
            print("❌ Failed to load font via QFontDatabase (ID -1).")
    except Exception as e:
        print(f"❌ Error adding application font: {e}")
else:
    print("❌ Font file does not exist for test.")

# Test Image Gen
try:
    print("Attempting to generate image...")
    out_path = ig.create_text_overlay_image(
        text="سلام پاکستان",
        font_path=font_path,
        font_size=50,
        text_color=(255, 0, 0),
        bg_color=(0, 0, 0),
        is_rtl=True
    )
    print(f"✅ Image generated at: {out_path}")
except Exception as e:
    print(f"❌ Image Generation Failed: {e}")
    import traceback
    traceback.print_exc()
