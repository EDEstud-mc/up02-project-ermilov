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
    total = len(cases)
    if not base_only:
        # None и строка вызывают TypeError; для 0.5 ожидается «мало».
        for qty, expected_error, expected_value in ((None, TypeError, None),
                                                    ("10", TypeError, None),
                                                    (0.5, None, "мало")):
            try:
                actual = _indicator(qty)
                success = expected_error is None and actual == expected_value
                detail = repr(actual)
            except Exception as error:
                success = expected_error is not None and type(error) is expected_error
                detail = type(error).__name__
            passed += int(success)
            total += 1
            expected = expected_error.__name__ if expected_error else repr(expected_value)
            print(f"{'OK' if success else 'FAIL'} qty={qty!r}: {detail} (ожидалось {expected})")
    print(f"Пройдено: {passed} / {total}")
    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", action="store_true", help="Только пять исходных тестов")
    args = parser.parse_args()
    raise SystemExit(0 if test_indicator(args.base) else 1)

