import argparse
import sqlite3
from decimal import Decimal
from pathlib import Path
from PIL import Image

import db_products as db
from config import DB_PATH
from catalog_data import ATTRIBUTES, FIELDS, product_image_path


def products():
    # Не создаём пустой файл вместо отсутствующей БД.
    if not Path(DB_PATH).is_file():
        raise FileNotFoundError(f"Не найдена БД: {DB_PATH}")
    return db.get_all_products()


def test_db_available():
    return isinstance(products(), list)


def test_products_count():
    rows = products()
    print(f"  Загружено товаров: {len(rows)}")
    return len(rows) > 0


def test_product_fields():
    with sqlite3.connect(Path(DB_PATH).resolve().as_uri() + "?mode=ro", uri=True) as connection:
        columns = tuple(row[1] for row in connection.execute('PRAGMA table_info("Товар")'))
    rows = products()
    return (columns == FIELDS and bool(rows)
            and all(all(hasattr(product, attr) for attr in ATTRIBUTES) for product in rows))


def test_prices_are_numbers():
    rows = products()
    return bool(rows) and all(
        isinstance(product.price, (int, float, Decimal))
        and not isinstance(product.price, bool)
        and Decimal(str(product.price)).is_finite()
        for product in rows
    )


def test_quantity_not_negative():
    rows = products()
    return bool(rows) and all(
        isinstance(product.quantity, int)
        and not isinstance(product.quantity, bool)
        and product.quantity >= 0
        for product in rows
    )


def test_names_not_empty():
    rows = products()
    return bool(rows) and all(
        isinstance(product.name, str) and bool(product.name.strip())
        for product in rows
    )


def test_has_image():
    for product in products():
        path = product_image_path(product.cover)
        if path and path.is_file():
            try:
                with Image.open(path) as image:
                    image.verify()
                print(f"  Читаемая обложка товара id={product.id}: {path.name}")
                return True
            except (OSError, ValueError):
                continue
    return False


def run_all_tests(base_only=False):
    tests = [
        ("БД доступна", test_db_available),
        ("Товары загружены", test_products_count),
        ("У товаров семь полей варианта 27", test_product_fields),
        ("Все цены — конечные числа", test_prices_are_numbers),
        ("Количество — целое и не отрицательное", test_quantity_not_negative),
    ]
    if not base_only:
        tests.append(("Названия не пустые", test_names_not_empty))
        tests.append(("Хотя бы у одного товара есть читаемая обложка", test_has_image))
    passed = 0
    for title, function in tests:
        try:
            success = bool(function())
        except Exception as error:
            print(f"  {type(error).__name__}: {error}")
            success = False
        passed += int(success)
        print(f"{'OK' if success else 'FAIL'} — {title}")
    print(f"Пройдено: {passed} / {len(tests)}")
    return passed == len(tests)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", action="store_true", help="Только пять исходных проверок")
    args = parser.parse_args()
    raise SystemExit(0 if run_all_tests(args.base) else 1)

