"""Добавляет надпись или значок на заглушку picture.png."""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont

base_dir = Path(__file__).resolve().parent
picture_path = base_dir / "resources" / "picture.png"

# Работаем с копией изображения в памяти.
with Image.open(picture_path) as source:
    image = source.convert("RGB")

image.thumbnail((200, 160), Image.Resampling.LANCZOS)
result = Image.new("RGB", (200, 200), "#FFFFFF")
result.paste(image, ((200 - image.width) // 2, (160 - image.height) // 2))
draw = ImageDraw.Draw(result)

# Arial на Windows или DejaVu Sans на других системах.
font_candidates = [
    str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf"),
    "DejaVuSans.ttf"
]
text_font = None
for font_path in font_candidates:
    try:
        text_font = ImageFont.truetype(font_path, 24)
        break
    except OSError:
        continue

if text_font:
    text = "Нет фото"
    box = draw.textbbox((0, 0), text, font=text_font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    draw.text(
        ((200 - text_width) // 2, 160 + (40 - text_height) // 2 - box[1]),
        text, font=text_font, fill="#000000"
    )
else:
    # Если шрифт не найден, используем значок фотоаппарата.
    draw.rounded_rectangle((76, 168, 124, 194), radius=4, outline="#000000", width=2)
    draw.rectangle((84, 164, 98, 168), fill="#000000")
    draw.ellipse((94, 174, 108, 188), outline="#000000", width=2)

result.save(picture_path, format="PNG")
print("Готово: resources/picture.png обновлён")


