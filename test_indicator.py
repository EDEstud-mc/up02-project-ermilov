import argparse
from catalog import _indicator

BASE_CASES = (
    (10, "много", "10 > 5"),
    (6, "много", "6 > 5"),
    (5, "мало", "5 <= 5 — граница"),
    (4, "мало", "4 <= 5"),
    (0, "мало", "0 <= 5"),
)
ADDED_CASES = (
    (100, "много", "большое число"),
    (1, "мало", "минимальное положительное целое"),
    (-1, "мало", "отрицательное число"),
)


def test_indicator(base_only=False):
    cases = BASE_CASES if base_only else BASE_CASES + ADDED_CASES
    passed = 0
    for qty, expected, comment in cases:
        try:
            actual = _indicator(qty)
            success = actual == expected
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            success = False
        passed += int(success)
        print(f"{'OK' if success else 'FAIL'} qty={qty}: {actual} "
              f"(ожидалось {expected}) — {comment}")
    print(f"Пройдено: {passed} / {len(cases)}")
    return passed == len(cases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", action="store_true", help="Только пять исходных тестов")
    args = parser.parse_args()
    raise SystemExit(0 if test_indicator(args.base) else 1)

