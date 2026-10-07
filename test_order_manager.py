import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import order_manager as orders
import migrate_orders
import backup_db
import error_handler


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "test.db"
        shutil.copyfile(orders.DB_PATH, self.path)
        self.addCleanup(patch.stopall)
        patch.object(orders, "DB_PATH", str(self.path)).start()
        patch.object(backup_db, "DB_PATH", str(self.path)).start()
        patch.object(error_handler.messagebox, "showerror").start()
        patch.object(error_handler.messagebox, "showwarning").start()
        self.before_stock = self.rows("SELECT id, количество FROM Товар")
        self.old_columns = {row[1] for row in self.rows("PRAGMA table_info(Заказ)")}
        self.old_orders = self.rows("SELECT id, дата, клиент FROM Заказ ORDER BY id")
        migrate_orders.migrate_orders()

    def rows(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute(query, args).fetchall()

    def execute(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(query, args)

    def counts(self):
        return (self.rows("SELECT COUNT(*) FROM Заказ")[0][0],
                self.rows("SELECT COUNT(*) FROM Состав_заказа")[0][0])

class OrderTests(DatabaseTests):
    def test_migration_preserves_orders_and_stock(self):
        self.assertEqual(self.rows("SELECT id, дата, клиент FROM Заказ ORDER BY id"), self.old_orders)
        self.assertEqual(self.rows("SELECT id, количество FROM Товар"), self.before_stock)
        self.assertEqual({r[1] for r in self.rows("PRAGMA table_info(Заказ)")}, {"id", "дата", "клиент"})
        self.assertEqual(self.rows("PRAGMA foreign_key_check"), [])

    def test_migration_can_be_repeated(self):
        counts = self.counts()
        migrate_orders.migrate_orders()
        self.assertEqual(self.counts(), counts)

    def test_multiple_items_and_fixed_price(self):
        order_id = orders.create_order("Клиент", [(1, None, 2, 100.25), (2, None, 1, 200)])
        self.assertIsInstance(order_id, int)
        self.assertEqual(len(orders.get_order_items(order_id)), 2)
        self.assertEqual(orders.get_order_total(order_id), Decimal("400.50"))
        self.assertEqual(self.rows("SELECT дата FROM Заказ WHERE id=?", (order_id,)),
                         [(datetime.now().strftime("%Y-%m-%d"),)])
        self.execute("UPDATE Товар SET цена=999999 WHERE id=1")
        self.assertEqual(orders.get_order_total(order_id), Decimal("400.50"))

    def test_empty_order_is_rejected(self):
        before = self.counts()
        self.assertIsNone(orders.create_order("Клиент", []))
        self.assertEqual(self.counts(), before)

    def test_invalid_quantity_price_and_size(self):
        before = self.counts()
        for size, quantity, price in ((None, 0, 100), (None, -1, 100),
                                      (None, True, 100), (None, 1.5, 100),
                                      (None, 1, -1), (None, 1, "nan"), (42, 1, 100)):
            with self.subTest(size=size, quantity=quantity, price=price):
                self.assertIsNone(orders.create_order("Клиент", [(1, size, quantity, price)]))
                self.assertEqual(self.counts(), before)

    def test_insufficient_duplicate_product_rolls_back(self):
        self.execute("UPDATE Товар SET количество=3 WHERE id=1")
        before = self.counts()
        self.assertIsNone(orders.create_order("Клиент", [(1, None, 2, 100), (1, None, 2, 100)]))
        self.assertEqual(orders.get_product_quantity(1), 3)
        self.assertEqual(self.counts(), before)

    def test_failure_on_second_item_rolls_back_first(self):
        stock = orders.get_product_quantity(1)
        before = self.counts()
        self.assertIsNone(orders.create_order("Клиент", [(1, None, 1, 100), (999999, None, 1, 100)]))
        self.assertEqual(orders.get_product_quantity(1), stock)
        self.assertEqual(self.counts(), before)

    def test_foreign_keys_are_enabled(self):
        with closing(orders.get_connection()) as connection:
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertIsNone(orders.add_order_item(999999, 1, None, 1, 100))

    def test_automatic_price_and_exact_stock_change(self):
        self.execute("UPDATE Товар SET количество=5 WHERE id=4")
        order_id = orders.create_order("Клиент", [(4, None, 2, None)])
        self.assertIsInstance(order_id, int)
        self.assertEqual(orders.get_product_quantity(4), 3)
        self.assertGreater(orders.get_order_total(order_id), 0)

    def test_backup_is_a_valid_database(self):
        path = backup_db.backup_database()
        with closing(sqlite3.connect(path)) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM Заказ").fetchone()[0], self.counts()[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
