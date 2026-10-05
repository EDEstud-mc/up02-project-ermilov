import argparse
import sqlite3
from decimal import Decimal
from pathlib import Path
from PIL import Image

from models import Product
from catalog_data import (
    FIELDS, prepare_product, indicator, is_low_stock,
    format_price, product_image_path
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "databases" / "db_variant_27.db"


def read_database():
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as connection:
        columns = [row[1] for row in connection.execute('PRAGMA table_info("Товар")')]
        rows = connection.execute('SELECT * FROM "Товар" ORDER BY id').fetchall()
    return columns, rows


def run_tests(extended=False):
    columns, rows = read_database()
    print(f"Всего товаров: {len(rows)}")
    checks = []

    def check(title, condition):
        checks.append(bool(condition))
        print(f"{'OK' if condition else 'FAIL'} — {title}")

    check("Порядок семи полей совпадает с вариантом 27", tuple(columns) == FIELDS)
    check("В базе есть товары", bool(rows))
    check("Каждая строка содержит семь полей", all(len(row) == 7 for row in rows))
    for row in rows:
        data = prepare_product(row)
        product = Product(product_id=row[0], genre=row[1], name=row[2],
                          developer=row[3], price=row[4], quantity=row[5], cover=row[6])
        check(f"Товар {row[0]}: объект Product и строка БД дают одинаковые поля",
              data == prepare_product(product))

    for quantity, expected_indicator, expected_red in (
        (0, "мало", True), (3, "мало", True), (4, "мало", False),
        (5, "мало", False), (6, "много", False)
    ):
        check(f"Остаток {quantity}: индикатор и подсветка",
              indicator(quantity) == expected_indicator and is_low_stock(quantity) == expected_red)

    edge = prepare_product((100, None, "   ", None, None, 0, None))
    check("Пустое название заменяется заглушкой", edge["name"] == "[Без названия]")
    check("Пустые жанр и разработчик заменяются заглушками",
          edge["genre"] == "[Без жанра]" and edge["developer"] == "[Без разработчика]")
    check("Цена None отображается как ноль", edge["price"] == 0)
    check("Нулевая цена форматируется как 0", format_price(0) == "0")
    check("Дробная цена сохраняет копейки", format_price(Decimal("12.50")) == "12,50")
    check("Пустая обложка передаётся как отсутствующее изображение",
          product_image_path(edge["cover"]) is None)

    if extended:
        check("У всех товаров есть цена, не None", all(row[4] is not None for row in rows))
        check("У всех товаров количество >= 0",
              all(isinstance(row[5], int) and row[5] >= 0 for row in rows))
        readable_images = []
        for row in rows:
            path = product_image_path(row[6])
            if path and path.is_file():
                try:
                    with Image.open(path) as image:
                        image.verify()
                    readable_images.append(path.name)
                except (OSError, ValueError):
                    print(f"Не читается изображение товара {row[0]}: {path.name}")
        check("Хотя бы у одного товара есть существующее читаемое изображение",
              bool(readable_images))
        if readable_images:
            print("Изображения:", ", ".join(readable_images))
        check("Цена больше миллиона читается корректно",
              format_price(1250000) == "1 250 000")
        long_name = "Очень длинное название видеоигры " * 5
        check("Название длиннее 100 символов сохраняется полностью",
              prepare_product((101, "RPG", long_name, "Студия", 0, 6, ""))["name"] == long_name.strip())
        check("Кириллическое название сохраняется",
              prepare_product((102, "RPG", "Ведьмак 3", "Студия", 0, 5, ""))["name"] == "Ведьмак 3")

    passed = sum(checks)
    print(f"Пройдено: {passed}/{len(checks)}")
    print("Результат:", "УСПЕХ" if passed == len(checks) else "ЕСТЬ ОШИБКИ")
    return passed == len(checks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extended", action="store_true", help="Проверки домашнего задания")
    args = parser.parse_args()
    raise SystemExit(0 if run_tests(args.extended) else 1)

