"""Проверка класса Product вручную."""
from models import Product


p = Product(
    product_id=1,
    genre="Экшен",
    name="GTA V",
    developer="Rockstar",
    price=2000,
    quantity=30,
    cover="gta.png"
)

# Выводим информацию
print(p.info())
print(f"Цена со скидкой 15%: {p.price_with_discount(15):.2f} руб.")
