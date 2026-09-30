"""Расширенное тестирование алгоритма скидки (Граничные случаи)."""
from datetime import datetime
from discount import calculate_price_with_discount


def print_test_report(passed, total):
    """Выводит красивый структурированный отчет о тестировании."""
    status = "✅ УСПЕХ" if passed == total else "❌ ЕСТЬ ОШИБКИ"
    print("=" * 40)
    print("ОТЧЁТ О ТЕСТИРОВАНИИ")
    print(f"Пройдено: {passed} / {total}")
    print(f"Результат: {status}")
    print("=" * 40)


def run_expanded_tests():
    test_cases = [
        
        (1, 5000, datetime(2026, 10, 1), 5000.0, "Граничный случай: 1-е число месяца"),
        
        
        (4, 2000, datetime(2026, 10, 31), 1500.0, "Граничный случай: последний день месяца"),
        
        
        (5, 0, datetime(2026, 10, 15), 0.0, "Граничный случай: нулевая цена товара"),
        
        
        (4, 4000, datetime(2026, 10, 15), 3000.0, "Граничный случай: отрицательное количество"),
        
        
        (1, 8000, datetime(2026, 11, 15), 6000.0, "Заказы только в позапрошлом месяце"),
    ]

    print("=" * 70)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ: ГРАНИЧНЫЕ СЛУЧАИ")
    print("=" * 70)

    passed = 0
    for product_id, price, date, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id} на {date.date()}: "
              f"{price} → {result} (ожидалось {expected}) — {comment}")

    print()
    
    print_test_report(passed, len(test_cases))


if __name__ == "__main__":
    run_expanded_tests()
