import os
import sqlite3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from catalog_data import product_image_path

base_dir = Path(__file__).resolve().parent
database = base_dir / "databases" / "db_variant_27.db"
with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as connection:
    product = connection.execute(
        'SELECT название, разработчик, обложка FROM Товар '
        'WHERE обложка IS NOT NULL AND обложка <> \'\' ORDER BY id LIMIT 1'
    ).fetchone()
if product is None:
    raise SystemExit("В БД нет товара с указанным именем обложки")
name, developer, cover = product
path = product_image_path(cover)
if path.exists():
    raise SystemExit(f"Файл уже существует и не заменён: {path}")
path.parent.mkdir(parents=True, exist_ok=True)
image = Image.new("RGB", (400, 400), "#D2F6E7")
draw = ImageDraw.Draw(image)
draw.rectangle((20, 20, 380, 380), outline="#70B2AF", width=6)
font_path = str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf")
title_font = None
for candidate in (font_path, "DejaVuSans.ttf"):
    try:
        title_font = ImageFont.truetype(candidate, 34)
        break
    except OSError:
        continue
title_font = title_font or ImageFont.load_default()
draw.text((40, 100), name or "GAME", font=title_font, fill="#000000")
draw.text((40, 170), developer or "", font=title_font, fill="#000000")
draw.text((40, 300), "DEMO COVER", font=title_font, fill="#000000")
image.save(path, format="PNG")
print(f"Учебное изображение создано: {path}")

