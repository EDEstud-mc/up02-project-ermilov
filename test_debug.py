import argparse
import os
import sqlite3
import sys
import tempfile
import tkinter as tk
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import db_products
import main_catalog
import resources
from catalog import _get_card_color, _indicator
from catalog_data import prepare_product, format_price
from config import DB_PATH

BASE_DIR = Path(__file__).resolve().parent


def sample(**changes):
    data = dict(id=1, genre="RPG", name="Игра", developer="Студия",
                price=1000, quantity=6, cover="")
    data.update(changes)
    return prepare_product(data)


def window_without_ui():
    window = main_catalog.CatalogWindow.__new__(main_catalog.CatalogWindow)
    window.root = Mock()
    window.catalog_frame = Mock()
    return window


class DebugTests(unittest.TestCase):
    def test_quantity_boundaries(self):
        cases = ((0, "#ff8080", "мало"), (3, "#ff8080", "мало"),
                 (4, "#FFFFFF", "мало"), (5, "#FFFFFF", "мало"),
                 (6, "#FFFFFF", "много"), (100, "#FFFFFF", "много"))
        for qty, color, indicator in cases:
            with self.subTest(qty=qty):
                self.assertEqual(_get_card_color(qty), color)
                self.assertEqual(_indicator(qty), indicator)

    def test_empty_name(self):
        for name in (None, "", "   "):
            self.assertEqual(sample(name=name)["name"], "[Без названия]")

    def test_empty_genre_and_developer(self):
        data = sample(genre=None, developer="")
        self.assertEqual(data["genre"], "[Без жанра]")
        self.assertEqual(data["developer"], "[Без разработчика]")

    def test_empty_and_zero_price(self):
        for price in (None, 0):
            self.assertEqual(format_price(sample(price=price)["price"]), "0")

    def test_cyrillic(self):
        self.assertEqual(sample(name="Ведьмак 3")["name"], "Ведьмак 3")

    def test_database_path_independent_of_cwd(self):
        self.assertTrue(Path(DB_PATH).is_absolute())
        before = db_products.get_all_products()
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as directory:
                os.chdir(directory)
                after = db_products.get_all_products()
        finally:
            os.chdir(previous)
        self.assertTrue(before)
        self.assertEqual([p.id for p in before], [p.id for p in after])

    def test_missing_cover_uses_placeholder(self):
        photo = object()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(resources.ImageTk, "PhotoImage", return_value=photo):
                result = resources.get_product_image(str(Path(directory) / "missing.png"))
        self.assertIs(result, photo)

    def test_corrupt_cover_uses_placeholder(self):
        photo = object()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.png"
            path.write_bytes(b"this is not a PNG image")
            with patch.object(resources.ImageTk, "PhotoImage", return_value=photo):
                self.assertIs(resources.get_product_image(str(path)), photo)

    def test_tk_image_failure_is_handled(self):
        path = str(BASE_DIR / "resources" / "gta.png")
        with patch.object(resources.ImageTk, "PhotoImage", side_effect=tk.TclError("test")):
            self.assertIsNone(resources.load_image(path))
            self.assertIsNone(resources.load_image_proportional(path))

    def test_missing_placeholder_returns_none(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(resources, "PATH_PICTURE", str(Path(directory) / "absent.png")):
                self.assertIsNone(resources.get_product_image(""))

    def test_empty_database_message(self):
        window = window_without_ui()
        with patch.object(main_catalog.db, "get_all_products", return_value=[]):
            with patch.object(main_catalog.tk, "Label") as label:
                window.load_products()
                self.assertIn("нет товаров", label.call_args.kwargs["text"])

    def test_database_error_message(self):
        window = window_without_ui()
        with patch.object(main_catalog.db, "get_all_products", side_effect=sqlite3.OperationalError("test")):
            with patch.object(main_catalog.messagebox, "showerror") as showerror:
                window.load_products()
                showerror.assert_called_once()

    def test_missing_database_does_not_create_file(self):
        window = window_without_ui()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "absent.db"
            with patch.object(main_catalog, "DB_PATH", str(path)):
                with patch.object(main_catalog.messagebox, "showerror") as showerror:
                    with patch.object(main_catalog.db, "get_all_products") as read:
                        window.load_products()
                        read.assert_not_called()
                        showerror.assert_called_once()
                        self.assertFalse(path.exists())

    def test_invalid_product_is_reported_and_next_is_processed(self):
        window = window_without_ui()
        products = [Mock(id=100), Mock(id=101)]
        with patch.object(main_catalog.db, "get_all_products", return_value=products):
            with patch.object(main_catalog, "create_product_card", side_effect=[ValueError("bad quantity"), None]) as create:
                with patch.object(main_catalog.messagebox, "showwarning") as warning:
                    window.load_products()
                    self.assertEqual(create.call_count, 2)
                    warning.assert_called_once()
                    self.assertIn("id=100", warning.call_args.args[1])


class HomeworkTests(unittest.TestCase):
    def test_long_name(self):
        name = "Очень длинное название видеоигры " * 5
        self.assertGreater(len(name), 100)
        self.assertEqual(sample(name=name)["name"], name.strip())

    def test_price_above_million(self):
        self.assertEqual(format_price(sample(price=1250000)["price"]), "1 250 000")

    def test_cyrillic_and_latin(self):
        name = "Ведьмак 3 — The Witcher 3: Wild Hunt"
        self.assertEqual(sample(name=name)["name"], name)


def save_report(result, student, extended):
    text = [
        "ОТЧЁТ ОБ ОТЛАДКЕ — ПАРА 15", f"Студент: {student}",
        f"Дата проверки: {datetime.now().strftime('%d.%m.%Y')}",
        "Вариант: 27 — магазин видеоигр", "",
        "Найденные ошибки в контрольных сценариях и исправления:",
        "1. Относительный путь БД зависел от папки запуска.",
        "   Исправление: абсолютный DB_PATH на основе __file__ в config.py.",
        "2. TclError от PhotoImage мог выйти из загрузчика изображения.",
        "   Исправление: обработка TclError; заглушка или [НЕТ ФОТО].",
        "3. Ошибка чтения БД могла прервать создание каталога.",
        "   Исправление: сообщение об ошибке; окно остаётся открытым.",
        "", f"Автоматические проверки: {result.testsRun} / {result.testsRun} — пройдены.",
        "Проверены границы 0, 3, 4, 5, 6, 100; пустое название; пустой жанр;",
        "пустой разработчик; цена None и 0; кириллица; отсутствующая и битая обложка;",
        "ошибка PhotoImage; отсутствие заглушки; пустой каталог; ошибка БД;",
        "отсутствие БД; обработка неверной записи и продолжение загрузки.",
        "Пустой состав: неприменимо — в БД варианта 27 этого поля нет.",
    ]
    if extended:
        text.extend(["ДЗ: название > 100 символов; цена > 1 000 000; кириллица + латиница."])
    text.extend([
        "", "Ручная проверка на ПК — заполни после просмотра окна:",
        "[ ] Все реальные игры просмотрены, ошибок отображения нет.",
        "[ ] Тестовые карточки крайних значений просмотрены.",
        "[ ] Картинка-заглушка и текст [НЕТ ФОТО] проверены.",
        "[ ] Длинное название, большая цена и смешанный текст читаются.",
        "[ ] Проверено изменение ширины окна и прокрутка.",
        "[ ] Точки останова и пошаговая отладка выполнены.",
        "[ ] В обычном запуске отсутствуют диагностические print.",
        "", "Вывод: автоматические проверки пройдены; ручной результат допиши выше."
    ])
    path = BASE_DIR / "debug_report.txt"
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    print(f"Отчёт сохранён: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extended", action="store_true", help="Три проверки ДЗ")
    parser.add_argument("--report", action="store_true", help="Создать debug_report.txt")
    parser.add_argument("--student", help="ФИО для отчёта")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DebugTests)
    if args.extended:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(HomeworkTests))
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if args.report:
        student = (args.student or input("Введи своё ФИО для отчёта: ")).strip()
        if not student:
            parser.error("ФИО не должно быть пустым")
        save_report(result, student, args.extended)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

