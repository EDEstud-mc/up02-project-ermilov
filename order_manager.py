import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from config import DB_PATH
from error_handler import safe_call


def get_connection():
    uri = Path(DB_PATH).resolve().as_uri() + "?mode=rw"
    connection = sqlite3.connect(uri, uri=True, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _check_quantity(quantity, allow_zero=False):
    minimum = 0 if allow_zero else 1
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < minimum:
        raise ValueError(f"Количество должно быть целым числом не меньше {minimum}")


def _add_order(connection, client, product_id, quantity):
    _check_quantity(quantity)
    client = str(client).strip()
    if not client:
        raise ValueError("Укажите ФИО клиента")
    order_date = datetime.now().strftime("%Y-%m-%d")
    cursor = connection.execute(
        "INSERT INTO Заказ (дата, клиент, товар_id, количество) VALUES (?, ?, ?, ?)",
        (order_date, client, product_id, quantity)
    )
    return cursor.lastrowid


def _update_quantity(connection, product_id, new_quantity):
    _check_quantity(new_quantity, allow_zero=True)
    cursor = connection.execute(
        "UPDATE Товар SET количество = ? WHERE id = ?", (new_quantity, product_id)
    )
    if cursor.rowcount != 1:
        raise ValueError("Товар не найден")
    return True


def _insert_only(client, product_id, quantity):
    with closing(get_connection()) as connection, connection:
        return _add_order(connection, client, product_id, quantity)


def add_order_to_db(client, product_id, quantity):
    """Учебная функция INSERT. Самостоятельно остаток не изменяет."""
    return safe_call(_insert_only, client, product_id, quantity)


def _set_quantity(product_id, new_quantity):
    with closing(get_connection()) as connection, connection:
        return _update_quantity(connection, product_id, new_quantity)


def update_product_quantity(product_id, new_quantity):
    """Учебная функция UPDATE. Не вызывайте второй раз после place_order."""
    return safe_call(_set_quantity, product_id, new_quantity)


def _read_value(query, parameters=()):
    with closing(get_connection()) as connection:
        row = connection.execute(query, parameters).fetchone()
    return row[0] if row else None


def get_last_order_id():
    return safe_call(_read_value, "SELECT MAX(id) FROM Заказ")


def get_product_quantity(product_id):
    return safe_call(_read_value, "SELECT количество FROM Товар WHERE id = ?", (product_id,))


def _place_order(client, product_id, quantity):
    _check_quantity(quantity)
    with closing(get_connection()) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT количество FROM Товар WHERE id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise ValueError("Товар не найден")
        if quantity > row[0]:
            raise ValueError(f"Доступно только {row[0]} шт.")
        order_id = _add_order(connection, client, product_id, quantity)
        _update_quantity(connection, product_id, row[0] - quantity)
        return order_id


def place_order(client, product_id, quantity=1):
    """Одно соединение, одна транзакция: INSERT + UPDATE, либо полный rollback."""
    return safe_call(_place_order, client, product_id, quantity)
