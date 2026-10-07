import argparse
import sqlite3
import sys
import tempfile
import tkinter as tk
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import catalog
import db_products
import discount
import error_handler
import main_catalog
from view_form import ViewForm


def sample(**changes):
    data = dict(id=4, genre="Стратегия", name="Тестовая игра",
                developer="Студия", price=2000, quantity=3, cover="")
    data.update(changes)
    return data


def form_without_ui(product=None, callback=None):
    form = ViewForm.__new__(ViewForm)
    form.window = Mock()
    form.product = product
    form.on_add_to_order = callback
    form.final_price = 1500
    form.quantity_var = Mock()
    form.quantity_var.get.return_value = "1"
    return form


class MainTests(unittest.TestCase):
    def test_safe_call_returns_result_and_passes_arguments(self):
        self.assertEqual(error_handler.safe_call(lambda a, b=0: a + b, 2, b=3), 5)

    def test_safe_call_error_types(self):
        cases = ((FileNotFoundError("file"), "showerror"),
                 (ConnectionError("connection"), "showerror"),
                 (sqlite3.OperationalError("db"), "showerror"),
                 (ValueError("value"), "showwarning"),
                 (RuntimeError("other"), "showerror"))
        for error, method in cases:
            with self.subTest(error=type(error).__name__):
                with patch.object(error_handler.messagebox, method) as popup:
                    self.assertIsNone(error_handler.safe_call(Mock(side_effect=error)))
                    popup.assert_called_once()

    def test_quantity_validation(self):
        for value, expected in (("1", (True, 1)), (" 25 ", (True, 25)),
                                ("0", (False, "Количество должно быть больше нуля")),
                                ("-1", (False, "Количество должно быть больше нуля")),
                                ("1.5", (False, "Количество должно быть целым числом")),
                                ("abc", (False, "Количество должно быть целым числом")),
                                ("", (False, "Количество должно быть целым числом"))):
            with self.subTest(value=value):
                self.assertEqual(error_handler.validate_positive_int(value, "Количество"), expected)

    def test_missing_callback(self):
        form = form_without_ui(sample())
        with patch.object(error_handler.messagebox, "showinfo") as info:
            form.add_to_order()
            self.assertIn("разработке", info.call_args.args[1])

    def test_missing_product(self):
        callback = Mock()
        form = form_without_ui(callback=callback)
        with patch.object(error_handler.messagebox, "showerror") as popup:
            form.add_to_order()
            callback.assert_not_called()
            self.assertEqual(popup.call_args.args[1], "Товар не выбран")

    def test_callback_exception_has_no_success_popup(self):
        form = form_without_ui(sample(), Mock(side_effect=ConnectionError("test")))
        with patch.object(error_handler.messagebox, "showerror") as error:
            with patch.object(error_handler.messagebox, "showinfo") as info:
                form.add_to_order()
                error.assert_called_once()
                info.assert_not_called()

    def test_callback_success(self):
        callback = Mock()
        form = form_without_ui(sample(), callback)
        with patch.object(error_handler.messagebox, "showinfo") as popup:
            form.add_to_order()
            self.assertIs(callback.call_args.args[0], form.product)
            popup.assert_called_once()

    def test_failed_price_does_not_add_product(self):
        callback = Mock()
        form = form_without_ui(sample(), callback)
        form.final_price = None
        with patch.object(error_handler.messagebox, "showerror"):
            form.add_to_order()
        callback.assert_not_called()

    def test_order_accumulates_and_checks_total_stock(self):
        window = main_catalog.CatalogWindow.__new__(main_catalog.CatalogWindow)
        window.order_items = {}
        product = sample(quantity=3)
        window.add_to_order(product, 2)
        window.add_to_order(product)
        self.assertEqual(window.order_items, {4: 3})
        with self.assertRaises(ValueError):
            window.add_to_order(product)
        self.assertEqual(window.order_items, {4: 3})
        for quantity in (0, -1, 1.5, True):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                window.add_to_order(product, quantity)

    def test_click_binding_recurses_and_skips_button(self):
        leaf, button = Mock(), Mock(spec=tk.Button)
        leaf.winfo_children.return_value = []
        middle = Mock()
        middle.winfo_children.return_value = [leaf, button]
        card = Mock()
        card.winfo_children.return_value = [middle]
        callback = Mock()
        catalog._bind_view_click(card, callback)
        leaf.bind.assert_called_once()
        button.bind.assert_not_called()
        leaf.bind.call_args.args[1](Mock())
        callback.assert_called_once()

    def test_discount_month_boundaries_and_decimal(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with sqlite3.connect(path) as connection:
                connection.execute("CREATE TABLE Заказ (товар_id INTEGER, дата TEXT)")
                connection.executemany("INSERT INTO Заказ VALUES (?, ?)",
                                       [(1, "2024-02-29"), (2, "2024-03-01"),
                                        (3, "2024-01-31"), (4, "2023-12-31")])
            with patch.object(discount, "DB_PATH", str(path)):
                date = datetime(2024, 3, 1)
                self.assertEqual(discount.calculate_price_with_discount(1, Decimal("2000"), date), 2000)
                self.assertEqual(discount.calculate_price_with_discount(2, 2000, date), 1500)
                self.assertEqual(discount.calculate_price_with_discount(3, 2000, date), 1500)
                self.assertEqual(discount.calculate_price_with_discount(4, 2000, datetime(2024, 1, 1)), 2000)
                self.assertEqual(discount.calculate_price_with_discount(9, 0, date), 0)

    def test_discount_missing_db_is_error_not_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.db"
            with patch.object(discount, "DB_PATH", str(path)):
                with patch.object(error_handler.messagebox, "showerror") as popup:
                    self.assertIsNone(discount.calculate_price_with_discount(1, 100))
                    popup.assert_called_once()
            self.assertFalse(path.exists())


class HomeworkTests(unittest.TestCase):
    def test_bad_quantity_does_not_call_callback(self):
        for value in ("", "0", "-1", "abc", "1.5"):
            with self.subTest(value=value):
                callback = Mock()
                form = form_without_ui(sample(), callback)
                form.quantity_var.get.return_value = value
                with patch.object(error_handler.messagebox, "showwarning") as popup:
                    form.add_to_order()
                    popup.assert_called_once()
                    callback.assert_not_called()

    def test_entered_quantity_is_forwarded(self):
        callback = Mock()
        form = form_without_ui(sample(), callback)
        form.quantity_var.get.return_value = "2"
        with patch.object(error_handler.messagebox, "showinfo"):
            form.add_to_order()
        callback.assert_called_once_with(form.product, 2)

    def test_all_product_queries_handle_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.db"
            with patch.object(db_products, "DB_PATH", str(path)):
                for func, args in ((db_products.get_all_products, ()),
                                   (db_products.get_products_by_category, ("Экшен",)),
                                   (db_products.get_products_low_stock, ())):
                    with self.subTest(func=func.__name__):
                        with patch.object(error_handler.messagebox, "showerror") as popup:
                            self.assertIsNone(func(*args))
                            popup.assert_called_once()
            self.assertFalse(path.exists())

    def test_orders_query_handles_missing_database(self):
        import db_orders
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.db"
            with patch.object(db_orders, "DB_PATH", str(path)):
                with patch.object(error_handler.messagebox, "showerror") as popup:
                    self.assertIsNone(db_orders.get_all_orders())
                    popup.assert_called_once()
            self.assertFalse(path.exists())


def gui_check():
    root = tk.Tk()
    root.withdraw()
    try:
        products = error_handler.safe_call(db_products.get_all_products)
        if not products:
            raise RuntimeError("Для проверки формы нужны товары из БД")
        order = main_catalog.CatalogWindow.__new__(main_catalog.CatalogWindow)
        order.order_items = {}
        form = ViewForm(root, products[0], order.add_to_order)
        print("Форма создана. Проверь поля, кнопки; затем нажми Назад.")
        root.wait_window(form.window)
        print("Заказ текущего сеанса:", order.order_items)
    finally:
        root.destroy()


def missing_database_check():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "missing.db"
        with patch.object(main_catalog, "DB_PATH", str(path)):
            window = main_catalog.CatalogWindow()
            print("Ожидается окно Ошибка БД. Закрой сообщение и каталог.")
            window.run()
        assert not path.exists(), "Не должна создаваться пустая БД"
    print("Проверка завершена. Настоящая БД не переименовывалась.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gui", action="store_true")
    group.add_argument("--missing-db", action="store_true")
    args = parser.parse_args()
    if args.gui:
        gui_check()
    elif args.missing_db:
        missing_database_check()
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(MainTests)
        if args.home:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(HomeworkTests))
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)
