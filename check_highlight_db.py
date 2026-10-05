import sqlite3
from pathlib import Path

from catalog import _get_card_color

DB_PATH = Path(__file__).resolve().parent / "databases" / "db_variant_27.db"


def read_products():
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as connection:
        return connection.execute(
            'SELECT id, жанр, название, разработчик, цена, количество, обложка '
            'FROM "Товар" ORDER BY id'
        ).fetchall()


def check_database():
    rows = read_products()
    if not rows:
        raise AssertionError("В таблице Товар нет товаров")
    highlighted = normal = failures = 0
    for row in rows:
        qty = row[5]
        if not isinstance(qty, int) or qty < 0:
            print(f"FAIL id={row[0]}: некорректное количество {qty!r}")
            failures += 1
            continue
        expected = "#ff8080" if qty <= 3 else "#FFFFFF"
        actual = _get_card_color(qty)
        success = actual.lower() == expected.lower()
        failures += int(not success)
        highlighted += int(actual.lower() == "#ff8080")
        normal += int(actual.lower() == "#ffffff")
        print(f"{'OK' if success else 'FAIL'} id={row[0]} | {row[2]} | "
              f"{qty} шт. | фон {actual}")
    print(f"Всего товаров: {len(rows)}")
    print(f"Подсвечено: {highlighted}")
    print(f"Без подсветки: {normal}")
    if failures:
        raise AssertionError(f"Ошибок: {failures}")
    print("Подсветка всех товаров БД проверена по данным")


if __name__ == "__main__":
    check_database()
