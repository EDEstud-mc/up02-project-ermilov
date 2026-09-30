import sqlite3
from datetime import datetime


def calculate_price_with_discount(product_id, price, date_context=None):
    """Вычисляет цену со скидкой 25%, если товар не заказывали в прошлом месяце."""
    if date_context is None:
        date_context = datetime.now()

    
    current_year = date_context.year
    current_month = date_context.month

    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year

    
    start_date = f"{prev_year}-{prev_month:02d}-01"
    end_date = f"{prev_year}-{prev_month:02d}-31"

    
    conn = sqlite3.connect("databases/db_variant_27.db")
    cursor = conn.cursor()

    
    cursor.execute("PRAGMA table_info(Заказ)")
    columns = [row[1].lower() for row in cursor.fetchall()]

    
    target_column = None
    for col in ["id_товара", "id_товар", "товар_id", "товар"]:
        if col in columns:
            target_column = col
            break

    
    if not target_column and len(columns) > 1:
        target_column = columns[1]

    
    query = f"""
        SELECT COUNT(*) FROM Заказ 
        WHERE `{target_column}` = ? AND дата BETWEEN ? AND ?
    """

    cursor.execute(query, (product_id, start_date, end_date))
    db_result = cursor.fetchone()
    
    
    count = db_result[0] if db_result else 0
    conn.close()

    
    if count == 0:
        return round(price * 0.75, 2)

    
    return float(price)
