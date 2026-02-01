import sys
import os
import json
import argparse
from PySide6.QtGui import QFont, QFontDatabase, QImage, QPainter, QColor, QPainterPath, QGuiApplication
from PySide6.QtCore import Qt, QRectF

# Set offscreen platform
os.environ["QT_QPA_PLATFORM"] = "offscreen"

def generate_image(args):
    # Init App (Required for QFont/QPainter)
    app = QGuiApplication.instance()
    if not app:
        app = QGuiApplication(sys.argv)

    # Decode arguments
    text = args['text']
    font_path = args.get('font_path')
    font_family = args.get('font_family', "Arial")
    font_size = args.get('font_size', 40)
    text_color = args.get('text_color', (255, 255, 255))
    bg_color = args.get('bg_color')
    bg_opacity = args.get('bg_opacity', 0.5)
    padding = args.get('padding', 20)
    corner_radius = args.get('corner_radius', 7.5)
    out_path = args['out_path']

    # Register custom font if provided
    current_font_family = font_family
    if font_path and os.path.exists(font_path):
        try:
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                current_font_family = families[0]
        except Exception as e:
            print(f"Error registering font: {e}", file=sys.stderr)

    font = QFont(current_font_family, font_size)
    font.setStyleStrategy(QFont.PreferAntialias)

    # Dummy painter to measure text
    temp_img = QImage(1, 1, QImage.Format_ARGB32)
    painter = QPainter(temp_img)
    painter.setFont(font)
    text_rect = painter.boundingRect(0, 0, 2000, 2000, Qt.AlignCenter | Qt.TextWordWrap, text)
    painter.end()

    img_width = text_rect.width() + int(padding * 2)
    img_height = text_rect.height() + int(padding * 2)

    img = QImage(img_width, img_height, QImage.Format_ARGB32)
    img.fill(Qt.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setFont(font)

    if bg_color:
        r, g, b = bg_color
        alpha = int(bg_opacity * 255)
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, img_width, img_height), corner_radius, corner_radius)
        painter.fillPath(path, QColor(r, g, b, alpha))

    painter.setPen(QColor(*text_color))
    draw_rect = QRectF(padding, padding, text_rect.width(), text_rect.height())
    painter.drawText(draw_rect, Qt.AlignCenter | Qt.TextWordWrap, text)
    painter.end()

    img.save(out_path)
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="JSON string of arguments")
    args = parser.parse_args()
    
    try:
        data = json.loads(args.json)
        generate_image(data)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
