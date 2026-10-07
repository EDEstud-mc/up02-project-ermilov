import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import order_manager as orders
import error_handler


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "test.db"
        shutil.copyfile(orders.DB_PATH, self.path)
        self.addCleanup(patch.stopall)
        patch.object(orders, "DB_PATH", str(self.path)).start()
        patch.object(error_handler.messagebox, "showerror").start()
        patch.object(error_handler.messagebox, "showwarning").start()

    def rows(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute(query, args).fetchall()

    def test_insert_and_date(self):
        order_id = orders.add_order_to_db("Тестовый клиент", 1, 2)
        self.assertIsInstance(order_id, int)
        self.assertEqual(self.rows("SELECT дата, клиент, товар_id, количество FROM Заказ WHERE id=?", (order_id,)),
                         [(datetime.now().strftime("%Y-%m-%d"), "Тестовый клиент", 1, 2)])
        self.assertEqual(orders.get_last_order_id(), order_id)

    def test_read_and_update_stock(self):
        self.assertTrue(orders.update_product_quantity(1, 3))
        self.assertEqual(orders.get_product_quantity(1), 3)
        self.assertIsNone(orders.update_product_quantity(1, -1))
        self.assertEqual(orders.get_product_quantity(1), 3)

    def test_place_order_updates_both_tables(self):
        before = orders.get_product_quantity(1)
        order_id = orders.place_order("Клиент", 1, 2)
        self.assertIsInstance(order_id, int)
        self.assertEqual(orders.get_product_quantity(1), before - 2)
        self.assertEqual(self.rows("SELECT количество FROM Заказ WHERE id=?", (order_id,)), [(2,)])

    def test_insufficient_stock_changes_nothing(self):
        before = orders.get_product_quantity(1)
        count = self.rows("SELECT COUNT(*) FROM Заказ")[0][0]
        self.assertIsNone(orders.place_order("Клиент", 1, before + 1))
        self.assertEqual(orders.get_product_quantity(1), before)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM Заказ")[0][0], count)

    def test_missing_product_and_invalid_quantity(self):
        for product_id, quantity in ((999999, 1), (1, 0), (1, -1), (1, 1.5), (1, True)):
            with self.subTest(product_id=product_id, quantity=quantity):
                self.assertIsNone(orders.place_order("Клиент", product_id, quantity))

    def test_failure_after_insert_rolls_back(self):
        before = self.rows("SELECT * FROM Заказ")
        stock = orders.get_product_quantity(1)
        with patch.object(orders, "_update_quantity", side_effect=sqlite3.OperationalError("test")):
            self.assertIsNone(orders.place_order("Клиент", 1, 1))
        self.assertEqual(self.rows("SELECT * FROM Заказ"), before)
        self.assertEqual(orders.get_product_quantity(1), stock)

    def test_all_available_products_on_copy(self):
        for product_id, stock in self.rows("SELECT id, количество FROM Товар"):
            if stock > 0:
                with self.subTest(product_id=product_id):
                    self.assertIsInstance(orders.place_order("Клиент", product_id), int)
                    self.assertEqual(orders.get_product_quantity(product_id), stock - 1)

    def test_missing_database_does_not_create_file(self):
        missing = Path(self.folder.name) / "absent.db"
        with patch.object(orders, "DB_PATH", str(missing)):
            self.assertIsNone(orders.place_order("Клиент", 1))
        self.assertFalse(missing.exists())


class QuantityTests(unittest.TestCase):
    def test_entry_validation(self):
        from error_handler import validate_positive_int
        for text in ("", "abc", "0", "-5", "1.5"):
            with self.subTest(text=text):
                self.assertFalse(validate_positive_int(text, "Количество")[0])
        self.assertEqual(validate_positive_int("2", "Количество"), (True, 2))

    def make_form(self):
        from unittest.mock import Mock
        from view_form import ViewForm
        form = ViewForm.__new__(ViewForm)
        form.window = Mock()
        form.product = object()
        form.data = {"id": 1}
        form.final_price = 100
        form.quantity_var = Mock()
        form.quantity_var.get.return_value = "2"
        form.client_var = Mock()
        form.client_var.get.return_value = "Тестовый клиент"
        form.on_add_to_order = Mock()
        return form

    def test_form_sends_client_and_entered_quantity(self):
        import view_form
        form = self.make_form()
        with patch.object(view_form, "get_product_quantity", return_value=5):
            with patch.object(view_form, "place_order", return_value=99) as save:
                with patch.object(error_handler.messagebox, "showinfo"):
                    form.add_to_order()
        save.assert_called_once_with("Тестовый клиент", 1, 2)
        form.on_add_to_order.assert_called_once_with()
        form.window.destroy.assert_called_once()

    def test_failed_save_has_no_success_and_keeps_form(self):
        import view_form
        form = self.make_form()
        with patch.object(view_form, "get_product_quantity", return_value=5):
            with patch.object(view_form, "place_order", return_value=None):
                with patch.object(error_handler.messagebox, "showinfo") as success:
                    form.add_to_order()
                    success.assert_not_called()
        form.on_add_to_order.assert_not_called()
        form.window.destroy.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
