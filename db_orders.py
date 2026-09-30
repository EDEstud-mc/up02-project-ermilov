"""Загрузка заказов из БД в объекты класса Order."""
import sqlite3
from config import DB_PATH
from models import Product, Order


def get_all_orders():
    """Возвращает список объектов Order, соединенных с объектами Product."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Запрос объединяет таблицы Заказ и Товар, вытаскивая все необходимые поля
    cur.execute("""
        SELECT 
            Заказ.id, Заказ.дата, Заказ.клиент, Заказ.количество,
            Товар.id, Товар.жанр, Товар.название, Товар.разработчик, 
            Товар.цена, Товар.количество, Товар.обложка
        FROM Заказ
        JOIN Товар ON Заказ.товар_id = Товар.id
        ORDER BY Заказ.id
    """)
    rows = cur.fetchall()
    conn.close()

    orders = []
    for row in rows:
        # 1. Собираем объект Product из полей с индексами 4-10
        product = Product(
            product_id=row[4],
            genre=row[5],
            name=row[6],
            developer=row[7],
            price=row[8],
            quantity=row[9],
            cover=row[10]
        )
        
        # 2. Создаем объект Order и передаем в него созданный выше product
        order = Order(
            order_id=row[0],
            date=row[1],
            client=row[2],
            product=product,
            quantity=row[3]
        )
        orders.append(order)
        
    return orders


def print_orders(orders):
    """Выводит список заказов в консоль."""
    print(f"\n{'=' * 75}")
    print(f"СПИСОК ВСЕХ ЗАКАЗОВ В БД ({len(orders)} шт.)")
    print(f"{'=' * 75}")
    
    for o in orders:
        print(o.info())
        print("-" * 75)


if __name__ == "__main__":
    all_orders = get_all_orders()
    print_orders(all_orders)
