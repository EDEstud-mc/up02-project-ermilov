"""Семь основных тестов подсветки из пары 14."""
from catalog import _get_card_color
from catalog_data import is_low_stock
from styles import COLOR_HIGHLIGHT, COLOR_MAIN_BG

TEST_CASES = (
    (10, "#FFFFFF", "10 > 3 — без подсветки"),
    (5, "#FFFFFF", "5 > 3 — без подсветки"),
    (4, "#FFFFFF", "4 > 3 — без подсветки"),
    (3, "#ff8080", "3 <= 3 — граница, подсветка"),
    (2, "#ff8080", "2 <= 3 — подсветка"),
    (1, "#ff8080", "1 <= 3 — подсветка"),
    (0, "#ff8080", "0 <= 3 — подсветка"),
)


def test_highlight():
    """Проверяет порог и точный цвет, а также согласованность модулей."""
    assert COLOR_HIGHLIGHT.lower() == "#ff8080", "Неверный COLOR_HIGHLIGHT"
    assert COLOR_MAIN_BG.lower() == "#ffffff", "Неверный COLOR_MAIN_BG"
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ПОДСВЕТКИ")
    print("=" * 70)
    passed = 0
    for qty, expected, comment in TEST_CASES:
        actual = _get_card_color(qty)
        expected_low_stock = expected.lower() == "#ff8080"
        success = (actual.lower() == expected.lower()
                   and is_low_stock(qty) == expected_low_stock)
        passed += int(success)
        print(f"{'OK' if success else 'FAIL'} qty={qty}: {actual} "
              f"(ожидалось {expected}) — {comment}")
    print("=" * 70)
    print(f"Пройдено: {passed} / {len(TEST_CASES)}")
    if passed != len(TEST_CASES):
        raise AssertionError("Есть ошибки подсветки")


if __name__ == "__main__":
    test_highlight()

