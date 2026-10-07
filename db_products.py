import sqlite3
from contextlib import closing
from pathlib import Path
from config import DB_PATH
from models import Product
from error_handler import safe_call


def _read_products(query, parameters=()):
    uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [Product(product_id=row[0], genre=row[1], name=row[2],
                    developer=row[3], price=row[4], quantity=row[5], cover=row[6])
            for row in rows]


def get_all_products():
    return safe_call(_read_products, "SELECT * FROM Товар ORDER BY id")


def get_products_by_category(category):
    return safe_call(_read_products,
                     "SELECT * FROM Товар WHERE жанр = ? ORDER BY id", (category,))


def get_products_low_stock():
    return safe_call(_read_products,
                     "SELECT * FROM Товар WHERE количество <= 3 ORDER BY id")


def print_catalog_with_highlight(products):
    if products is None:
        print("Каталог не прочитан: см. сообщение об ошибке")
        return
    print(f"КАТАЛОГ ({len(products)} товаров)")
    for product in products:
        highlight = "⚠️" if product.quantity <= 3 else "  "
        print(f"{highlight} {product.info()}")


if __name__ == "__main__":
    print_catalog_with_highlight(get_all_products())
    print_catalog_with_highlight(get_products_by_category("Экшен"))
    print_catalog_with_highlight(get_products_low_stock())
