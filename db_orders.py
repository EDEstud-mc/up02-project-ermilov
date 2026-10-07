import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from config import DB_PATH
from models import Product
from error_handler import safe_call


@dataclass
class Order:
    # В текущем models.py нет Order; сохраняем отдельную модель здесь.
    order_id: int
    date: str
    client: str
    product: Product
    quantity: int

    def info(self):
        return (f"Заказ №{self.order_id}: {self.date}, {self.client}; "
                f"{self.product.name} × {self.quantity} шт.")


def _read_orders():
    uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        rows = connection.execute("""
            SELECT Заказ.id, Заказ.дата, Заказ.клиент, Заказ.количество,
                   Товар.id, Товар.жанр, Товар.название, Товар.разработчик,
                   Товар.цена, Товар.количество, Товар.обложка
            FROM Заказ JOIN Товар ON Заказ.товар_id = Товар.id
            ORDER BY Заказ.id
        """).fetchall()
    return [Order(row[0], row[1], row[2],
                  Product(product_id=row[4], genre=row[5], name=row[6],
                          developer=row[7], price=row[8], quantity=row[9],
                          cover=row[10]), row[3]) for row in rows]


def get_all_orders():
    return safe_call(_read_orders)


def print_orders(orders):
    if orders is None:
        print("Заказы не прочитаны: см. сообщение об ошибке")
        return
    print(f"СПИСОК ЗАКАЗОВ ({len(orders)} шт.)")
    for order in orders:
        print(order.info())


if __name__ == "__main__":
    print_orders(get_all_orders())
