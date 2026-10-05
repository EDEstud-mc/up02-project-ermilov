from catalog import _indicator
from catalog_data import indicator

TEST_CASES = (
    (10, "много", "10 > 5"),
    (6, "много", "6 > 5, граница"),
    (5, "мало", "5 <= 5, граница"),
    (4, "мало", "4 <= 5"),
    (1, "мало", "1 <= 5"),
    (0, "мало", "0 <= 5"),
    (100, "много", "большое число"),
    (1000, "много", "ДЗ: большое число"),
    (50, "много", "ДЗ: среднее значение"),
    (5, "мало", "ДЗ: повторная проверка границы"),
    (6, "много", "ДЗ: повторная проверка границы"),
    (-1, "мало", "ДЗ: -1 <= 5"),
)


def test_indicator():
    """Проверяет функцию карточки и согласованность с catalog_data."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНДИКАТОРА")
    print("=" * 60)
    passed = 0
    for qty, expected, comment in TEST_CASES:
        result = _indicator(qty)
        data_result = indicator(qty)
        success = result == expected and data_result == expected
        passed += int(success)
        status = "OK" if success else "FAIL"
        print(f"{status} qty={qty}: {result} (ожидалось {expected}) — {comment}")
        if data_result != expected:
            print(f"  catalog_data.indicator вернул {data_result!r}")
    print("=" * 60)
    print(f"Пройдено: {passed} / {len(TEST_CASES)}")
    if passed != len(TEST_CASES):
        raise AssertionError("Есть ошибки индикатора")


if __name__ == "__main__":
    test_indicator()

