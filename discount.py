"""Модуль расчёта скидки."""
from datetime import datetime, timedelta
import sqlite3
# Если файла config.py нет, можно временно указать путь строкой: DB_PATH = "db_variant_27.db"
from config import DB_PATH


def get_previous_month_range(date):
    """
    Возвращает (начало, конец) предыдущего месяца.
    
    :param date: дата расчёта
    :return: (start_date, end_date) в формате YYYY-MM-DD
    """
    first_day = date.replace(day=1)
    last_day_prev = first_day - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    return (
        first_day_prev.strftime("%Y-%m-%d"),
        last_day_prev.strftime("%Y-%m-%d")
    )


def has_orders_in_previous_month(product_id, date):
    """
    Есть ли заказы товара в предыдущем месяце?
    
    :param product_id: id товара
    :param date: дата расчёта
    :return: True / False
    """
    start, end = get_previous_month_range(date)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Делаем запрос к вашей таблице "Заказ"
    cur.execute(
        "SELECT COUNT(*) FROM Заказ "
        "WHERE товар_id = ? AND дата BETWEEN ? AND ?",
        (product_id, start, end)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def calculate_price_with_discount(product_id, price, date):
    """
    Рассчитывает цену со скидкой 25%.
    
    :param product_id: id товара
    :param price: базовая цена
    :param date: дата расчёта
    :return: цена со скидкой или без
    """
    if has_orders_in_previous_month(product_id, date):
        return price
    return price * 0.75
