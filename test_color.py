import argparse
from catalog import _get_card_color
from styles import COLOR_HIGHLIGHT, COLOR_MAIN_BG

BASE_CASES = (
    (10, COLOR_MAIN_BG, "10 > 3"),
    (5, COLOR_MAIN_BG, "5 > 3"),
    (4, COLOR_MAIN_BG, "4 > 3"),
    (3, COLOR_HIGHLIGHT, "3 <= 3 — граница"),
    (2, COLOR_HIGHLIGHT, "2 <= 3"),
    (0, COLOR_HIGHLIGHT, "0 <= 3"),
)
ADDED_CASES = (
    (100, COLOR_MAIN_BG, "большое число"),
    (-1, COLOR_HIGHLIGHT, "отрицательное число"),
)


def test_color(base_only=False):
    if COLOR_HIGHLIGHT.lower() != "#ff8080" or COLOR_MAIN_BG.lower() != "#ffffff":
        print("FAIL — константы цветов не соответствуют КИМ")
        return False
    cases = BASE_CASES if base_only else BASE_CASES + ADDED_CASES
    passed = 0
    for qty, expected, comment in cases:
        try:
            actual = _get_card_color(qty)
            success = actual.lower() == expected.lower()
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
    parser.add_argument("--base", action="store_true", help="Только шесть исходных тестов")
    args = parser.parse_args()
    raise SystemExit(0 if test_color(args.base) else 1)

