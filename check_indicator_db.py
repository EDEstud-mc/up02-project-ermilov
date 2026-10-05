"""Проверяет остатки варианта 27. Открывает БД только для чтения."""
import sqlite3
from pathlib import Path

from catalog import _indicator

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
    many = few = 0
    failures = 0
    for row in rows:
        qty = row[5]
        if not isinstance(qty, int) or qty < 0:
            print(f"FAIL id={row[0]}: некорректный остаток {qty!r}")
            failures += 1
            continue
        actual = _indicator(qty)
        expected = "много" if qty > 5 else "мало"
        success = actual == expected
        failures += int(not success)
        status = "OK" if success else "FAIL"
        print(f"{status} id={row[0]} | {row[2]} | {qty} шт. | {actual}")
        many += int(actual == "много")
        few += int(actual == "мало")
    print(f"Всего товаров: {len(rows)}")
    print(f"С «много»: {many}")
    print(f"С «мало»: {few}")
    if failures:
        raise AssertionError(f"Ошибок: {failures}")
    print("Все индикаторы в БД проверены")


if __name__ == "__main__":
    check_database()

