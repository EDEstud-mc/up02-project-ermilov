from datetime import datetime
from models import Product

print("--- ЗАПУСК 5 ДОПОЛНИТЕЛЬНЫХ ТЕСТОВ ---")


p1 = Product(product_id=1, name="Экшен-игра", genre="Action", price=3000, quantity=5)
date1 = datetime(2026, 9, 25)

print("\n[Тест 1]")
print(f"Базовая цена (Товар 1): {p1.price}")
print(f"Со скидкой на {date1.strftime('%Y-%m-%d')}: {p1.price_with_discount_auto(date1)}")



p2 = Product(product_id=2, name="Ролевая игра", genre="RPG", price=4500, quantity=2)
date2 = datetime(2026, 10, 10)

print("\n[Тест 2]")
print(f"Базовая цена (Товар 2): {p2.price}")
print(f"Со скидкой на {date2.strftime('%Y-%m-%d')}: {p2.price_with_discount_auto(date2)}")



p3 = Product(product_id=3, name="Стратегия", genre="Strategy", price=1200, quantity=10)
date3 = datetime(2027, 1, 15)

print("\n[Тест 3]")
print(f"Базовая цена (Товар 3): {p3.price}")
print(f"Со скидкой на {date3.strftime('%Y-%m-%d')}: {p3.price_with_discount_auto(date3)}")



p4 = Product(product_id=4, name="Коллекционное издание", genre="Приключения", price=25000, quantity=1)
date4 = datetime(2026, 5, 1)

print("\n[Тест 4]")
print(f"Базовая цена (Товар 4): {p4.price}")
print(f"Со скидкой на {date4.strftime('%Y-%m-%d')}: {p4.price_with_discount_auto(date4)}")



p5 = Product(product_id=5, name="Инди-симулятор", genre="Simulator", price=800, quantity=4)
date5 = datetime(2026, 8, 20)

print("\n[Тест 5]")
print(f"Базовая цена (Товар 5): {p5.price}")
print(f"Со скидкой на {date5.strftime('%Y-%m-%d')}: {p5.price_with_discount_auto(date5)}")
