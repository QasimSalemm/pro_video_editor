import os
import sys
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

font_path = os.path.join("fonts", "Noto Nastaliq Urdu Regular.ttf")
print(f"Checking font path: {os.path.abspath(font_path)}")

if not os.path.exists(font_path):
    print("❌ Font file NOT found!")
    sys.exit(1)

try:
    print("Attempting to load font...")
    font = ImageFont.truetype(font_path, 40)
    print("✅ Font loaded successfully!")
    
    text = "سلام پاکستان"
    print(f"Original Text: {text}")
    
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(f"Processed Text: {bidi_text}")
    
    img = Image.new('RGB', (300, 100), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), bidi_text, font=font, fill=(0, 0, 0))
    print("✅ Text drawn successfully (in memory).")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
