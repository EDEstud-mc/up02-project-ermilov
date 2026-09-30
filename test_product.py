from datetime import datetime
from models import Product

# Используем ID=1 (как в первой строке вашей таблицы "Заказ")
p = Product(product_id=1, name="Тестовая игра", genre="RPG", price=15000, quantity=3)

# Используем дату 15 сентября 2026 года из вашей БД
date = datetime(2026, 9, 15)

print(f"Базовая цена: {p.price}")
print(f"Со скидкой: {p.price_with_discount_auto(date)}")
