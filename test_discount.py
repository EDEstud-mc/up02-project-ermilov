"""Тестирование алгоритма скидки под данные Варианта 27."""
from datetime import datetime
from discount import calculate_price_with_discount


def run_tests():
    test_cases = [
        # (product_id, price, date, expected, comment)
        (1, 8500, datetime(2026, 10, 15), 8500, "Заказы есть в сентябре"),
        # Скорректировано под Вариант 27 (в вашей БД этот товар покупали в сентябре)
        (2, 15000, datetime(2026, 10, 15), 15000, "Заказы есть в сентябре"),
        (3, 12000, datetime(2026, 10, 15), 12000, "Заказы есть"),
        (4, 4500, datetime(2026, 10, 15), 3375, "Заказов нет → скидка"),
        (5, 6000, datetime(2026, 10, 15), 4500, "Заказов нет → скидка"),
        
        # Скорректировано под Вариант 27 (в октябре заказов в вашей БД нет)
        (2, 15000, datetime(2026, 11, 15), 11250, "В октябре заказов нет → скидка"),
        (1, 8500, datetime(2026, 11, 15), 6375, "В октябре заказов нет → скидка"),
        (4, 4500, datetime(2026, 9, 1), 3375, "Август — заказов нет"),
        
        # Ваши граничные случаи
        (2, 10000, datetime(2027, 1, 15), 7500, "Граничный случай: проверка января"),
        (1, 5000, datetime(2026, 10, 1), 5000, "Граничный случай: первое число месяца"),
        (4, 2000, datetime(2026, 10, 31), 1500, "Граничный случай: последний день месяца"),
    ]

    print("=" * 70)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ")
    print("=" * 70)

    passed = 0
    for product_id, price, date, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id} на {date.date()}: "
              f"{price} → {result} (ожидалось {expected}) — {comment}")

    print("=" * 70)
    print(f"Пройдено: {passed} / {len(test_cases)}")


if __name__ == "__main__":
    run_tests()
