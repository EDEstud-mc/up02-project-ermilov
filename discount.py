import sqlite3
from datetime import datetime


def calculate_price_with_discount(product_id, price, date_context=None):
    """Вычисляет цену со скидкой 25%, если товар не заказывали в прошлом месяце."""
    if date_context is None:
        date_context = datetime.now()

    # Определение границ предыдущего месяца
    current_year = date_context.year
    current_month = date_context.month

    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year

    # Форматируем даты для SQL-запроса BETWEEN
    start_date = f"{prev_year}-{prev_month:02d}-01"
    end_date = f"{prev_year}-{prev_month:02d}-31"

    # Подключение к базе данных
    conn = sqlite3.connect("databases/db_variant_27.db")
    cursor = conn.cursor()

    # Извлекаем ИМЯ колонки (оно находится строго на индексе 1 в ответе PRAGMA)
    cursor.execute("PRAGMA table_info(Заказ)")
    columns = [row[1].lower() for row in cursor.fetchall()]

    # Ищем подходящее имя колонки для ID товара
    target_column = None
    for col in ["id_товара", "id_товар", "товар_id", "товар"]:
        if col in columns:
            target_column = col
            break

    # Если совпадений нет, берем вторую колонку по счету (индекс 1)
    if not target_column and len(columns) > 1:
        target_column = columns[1]

    # Выполняем SQL-запрос к БД
    query = f"""
        SELECT COUNT(*) FROM Заказ 
        WHERE `{target_column}` = ? AND дата BETWEEN ? AND ?
    """

    cursor.execute(query, (product_id, start_date, end_date))
    db_result = cursor.fetchone()
    
    # Извлекаем число из кортежа БД (индекс 0)
    count = db_result[0] if db_result else 0
    conn.close()

    # Если заказов в прошлом месяце не было (count == 0) -> скидка 25%
    if count == 0:
        return round(price * 0.75, 2)

    # Если заказы были -> возвращаем базовую цену
    return float(price)
