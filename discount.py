import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from config import DB_PATH
from error_handler import safe_call


def _calculate_price(product_id, price, date_context=None):
    try:
        amount = Decimal(str(price))
    except InvalidOperation as error:
        raise ValueError("Цена должна быть числом") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError("Цена должна быть конечным неотрицательным числом")
    current = date_context or datetime.now()
    current_start = current.date().replace(day=1)
    previous_start = (current_start - timedelta(days=1)).replace(day=1)
    # mode=ro не создаёт пустую БД при неверном пути.
    uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM Заказ "
            "WHERE товар_id = ? AND дата >= ? AND дата < ?",
            (product_id, previous_start.isoformat(), current_start.isoformat())
        ).fetchone()[0]
    if count == 0:
        amount *= Decimal("0.75")
    return float(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_price_with_discount(product_id, price, date_context=None):
    """При ошибке возвращает None; это не бесплатный товар и не нулевая цена."""
    return safe_call(_calculate_price, product_id, price, date_context)
