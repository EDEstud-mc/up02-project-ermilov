import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
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


def _money(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Цена должна быть числом") from error
    if not result.is_finite() or result < 0:
        raise ValueError("Цена должна быть конечной и неотрицательной")
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _date(value=None):
    value = value or datetime.now().strftime("%Y-%m-%d")
    parsed = datetime.strptime(value, "%Y-%m-%d")
    if parsed.strftime("%Y-%m-%d") != value:
        raise ValueError("Дата должна иметь формат YYYY-MM-DD")
    return value


def _add_header(connection, client, order_date):
    client = str(client).strip()
    if not client:
        raise ValueError("Укажите ФИО клиента")
    return connection.execute(
        "INSERT INTO Заказ(дата, клиент) VALUES (?, ?)", (order_date, client)
    ).lastrowid


def _add_item(connection, order_id, product_id, size, quantity, price):
    _check_quantity(quantity)
    if size not in (None, "", "—"):
        raise ValueError("У видеоигр нет размеров")
    return connection.execute(
        "INSERT INTO Состав_заказа(заказ_id, товар_id, размер, количество, цена) "
        "VALUES (?, ?, NULL, ?, ?)",
        (order_id, product_id, quantity, float(_money(price)))
    ).lastrowid


def _insert_header(client, order_date=None):
    with closing(get_connection()) as connection, connection:
        return _add_header(connection, client, _date(order_date))


def add_order_to_db(client, date=None):
    """Учебный INSERT заголовка; интерфейс использует комплексную create_order."""
    return safe_call(_insert_header, client, date)


def _insert_item(order_id, product_id, size, quantity, price):
    with closing(get_connection()) as connection, connection:
        return _add_item(connection, order_id, product_id, size, quantity, price)


def add_order_item(order_id, product_id, size, quantity, price):
    """Учебный INSERT позиции без списания; не вызывается отдельно в интерфейсе."""
    return safe_call(_insert_item, order_id, product_id, size, quantity, price)


def _checkout_price(connection, product_id, base_price, order_date):
    current_start = datetime.strptime(order_date, "%Y-%m-%d").date().replace(day=1)
    previous_start = (current_start - timedelta(days=1)).replace(day=1)
    count = connection.execute(
        "SELECT COUNT(*) FROM Заказ JOIN Состав_заказа ON Заказ.id=Состав_заказа.заказ_id "
        "WHERE Состав_заказа.товар_id=? AND дата>=? AND дата<?",
        (product_id, previous_start.isoformat(), current_start.isoformat())
    ).fetchone()[0]
    amount = _money(base_price)
    return _money(amount * Decimal("0.75") if count == 0 else amount)


def _decrease(connection, product_id, quantity):
    _check_quantity(quantity)
    cursor = connection.execute(
        "UPDATE Товар SET количество=количество-? WHERE id=? AND количество>=?",
        (quantity, product_id, quantity)
    )
    if cursor.rowcount != 1:
        raise ValueError(f"Недостаточно товара id={product_id}")


def _decrease_only(product_id, quantity):
    with closing(get_connection()) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        _decrease(connection, product_id, quantity)
    return True


def decrease_product_quantity(product_id, quantity):
    """Для отдельного учебного UPDATE; не вызывайте после create_order."""
    return safe_call(_decrease_only, product_id, quantity) is True


def _create_order(client, items, order_date=None):
    if not items:
        raise ValueError("Добавьте хотя бы одну позицию")
    order_date = _date(order_date)
    with closing(get_connection()) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        order_id = _add_header(connection, client, order_date)
        for product_id, size, quantity, price in items:
            _check_quantity(quantity)
            row = connection.execute("SELECT цена FROM Товар WHERE id=?", (product_id,)).fetchone()
            if row is None:
                raise ValueError(f"Товар id={product_id} не найден")
            # None означает: пересчитать цену прямо при оформлении корзины.
            if price is None:
                price = _checkout_price(connection, product_id, row[0], order_date)
            _add_item(connection, order_id, product_id, size, quantity, price)
            _decrease(connection, product_id, quantity)
        return order_id


def create_order(client, items, date=None):
    """items: (product_id, None, quantity, price); один commit на все позиции."""
    return safe_call(_create_order, client, items, date)


def _read_rows(query, parameters=()):
    with closing(get_connection()) as connection:
        return connection.execute(query, parameters).fetchall()


def get_all_orders():
    return safe_call(_read_rows, "SELECT id, дата, клиент FROM Заказ ORDER BY id DESC")


def get_order_items(order_id):
    return safe_call(_read_rows, """
        SELECT Состав_заказа.id, Товар.название, Состав_заказа.размер,
               Состав_заказа.количество, Состав_заказа.цена
        FROM Состав_заказа JOIN Товар ON Состав_заказа.товар_id=Товар.id
        WHERE заказ_id=? ORDER BY Состав_заказа.id
    """, (order_id,))


def get_order_total(order_id):
    rows = safe_call(_read_rows,
                     "SELECT количество, цена FROM Состав_заказа WHERE заказ_id=?", (order_id,))
    if rows is None:
        return None
    return sum((quantity * _money(price) for quantity, price in rows), Decimal("0.00"))


def get_product_quantity(product_id):
    rows = safe_call(_read_rows, "SELECT количество FROM Товар WHERE id=?", (product_id,))
    return rows[0][0] if rows else None


def get_last_order_id():
    rows = safe_call(_read_rows, "SELECT MAX(id) FROM Заказ")
    return rows[0][0] if rows else None


def _set_quantity(product_id, new_quantity):
    _check_quantity(new_quantity, allow_zero=True)
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute("UPDATE Товар SET количество=? WHERE id=?", (new_quantity, product_id))
        if cursor.rowcount != 1:
            raise ValueError("Товар не найден")
    return True


def update_product_quantity(product_id, new_quantity):
    return safe_call(_set_quantity, product_id, new_quantity)
