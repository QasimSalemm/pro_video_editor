import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

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
    Creates a text overlay image using Pillow.
    """
    # Load Font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Fallback to a default font if path doesn't exist
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Create a dummy image to measure text size
    # In newer Pillow versions, use font.getbbox() or font.getlength()
    dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Final image size includes padding
    img_width = int(text_w + padding * 2)
    img_height = int(text_h + padding * 2)

    # Create final image
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded background rectangle with alpha
    if bg_color:
        r, g, b = bg_color
        alpha = int(bg_opacity * 255)
        # Pillow's rounded_rectangle uses [x0, y0, x1, y1]
        bg_shape = [padding/2, padding/2, img_width - padding/2, img_height - padding/2]
        draw.rounded_rectangle(bg_shape, radius=corner_radius, fill=(r, g, b, alpha))

    # Draw centered text
    # text_color is RGB, add alpha 255
    full_text_color = (*text_color, 255)
    
    # Calculate text position to center it within the padded area
    text_x = (img_width - text_w) / 2
    text_y = (img_height - text_h) / 2 - bbox[1] # Adjust for baseline
    
    draw.text((text_x, text_y), text, font=font, fill=full_text_color)

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    temp_file.close()
    return temp_file.name
