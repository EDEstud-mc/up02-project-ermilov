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
        self.path = Path(self.folder.name) / 'test.db'
        shutil.copyfile(orders.DB_PATH, self.path)
        self.addCleanup(patch.stopall)
        patch.object(orders, 'DB_PATH', str(self.path)).start()
        patch.object(backup_db, 'DB_PATH', str(self.path)).start()
        patch.object(error_handler.messagebox, 'showerror').start()
        patch.object(error_handler.messagebox, 'showwarning').start()
        self.before_stock = self.rows('SELECT id, количество FROM Товар')
        self.old_columns = {row[1] for row in self.rows('PRAGMA table_info(Заказ)')}
        self.old_orders = self.rows('SELECT id, дата, клиент FROM Заказ ORDER BY id')
        migrate_orders.migrate_orders()
        import migrate_users
        import database
        migrate_users.migrate_users()
        self.actor = database.get_user_by_login('admin1')

    def rows(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute(query, args).fetchall()

    def execute(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(query, args)

    def counts(self):
        return (self.rows('SELECT COUNT(*) FROM Заказ')[0][0], self.rows('SELECT COUNT(*) FROM Состав_заказа')[0][0])

class OrderTests(DatabaseTests):

    def test_migration_preserves_orders_and_stock(self):
        self.assertEqual(self.rows('SELECT id, дата, клиент FROM Заказ ORDER BY id'), self.old_orders)
        self.assertEqual(self.rows('SELECT id, количество FROM Товар'), self.before_stock)
        self.assertEqual({r[1] for r in self.rows('PRAGMA table_info(Заказ)')}, {'id', 'дата', 'клиент'})
        self.assertEqual(self.rows('PRAGMA foreign_key_check'), [])

    def test_migration_can_be_repeated(self):
        counts = self.counts()
        migrate_orders.migrate_orders()
        self.assertEqual(self.counts(), counts)

    def test_multiple_items_and_fixed_price(self):
        order_id = orders.create_order('Клиент', [(1, None, 2, 100.25), (2, None, 1, 200)], current_user=self.actor)
        self.assertIsInstance(order_id, int)
        self.assertEqual(len(orders.get_order_items(order_id, current_user=self.actor)), 2)
        self.assertEqual(orders.get_order_total(order_id, current_user=self.actor), Decimal('400.50'))
        self.assertEqual(self.rows('SELECT дата FROM Заказ WHERE id=?', (order_id,)), [(datetime.now().strftime('%Y-%m-%d'),)])
        self.execute('UPDATE Товар SET цена=999999 WHERE id=1')
        self.assertEqual(orders.get_order_total(order_id, current_user=self.actor), Decimal('400.50'))

    def test_empty_order_is_rejected(self):
        before = self.counts()
        self.assertIsNone(orders.create_order('Клиент', [], current_user=self.actor))
        self.assertEqual(self.counts(), before)

    def test_invalid_quantity_price_and_size(self):
        before = self.counts()
        for size, quantity, price in ((None, 0, 100), (None, -1, 100), (None, True, 100), (None, 1.5, 100), (None, 1, -1), (None, 1, 'nan'), (42, 1, 100)):
            with self.subTest(size=size, quantity=quantity, price=price):
                self.assertIsNone(orders.create_order('Клиент', [(1, size, quantity, price)], current_user=self.actor))
                self.assertEqual(self.counts(), before)

    def test_insufficient_duplicate_product_rolls_back(self):
        self.execute('UPDATE Товар SET количество=3 WHERE id=1')
        before = self.counts()
        self.assertIsNone(orders.create_order('Клиент', [(1, None, 2, 100), (1, None, 2, 100)], current_user=self.actor))
        self.assertEqual(orders.get_product_quantity(1), 3)
        self.assertEqual(self.counts(), before)

    def test_failure_on_second_item_rolls_back_first(self):
        stock = orders.get_product_quantity(1)
        before = self.counts()
        self.assertIsNone(orders.create_order('Клиент', [(1, None, 1, 100), (999999, None, 1, 100)], current_user=self.actor))
        self.assertEqual(orders.get_product_quantity(1), stock)
        self.assertEqual(self.counts(), before)

    def test_foreign_keys_are_enabled(self):
        with closing(orders.get_connection()) as connection:
            self.assertEqual(connection.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        self.assertIsNone(orders.add_order_item(999999, 1, None, 1, 100))

    def test_automatic_price_and_exact_stock_change(self):
        self.execute('UPDATE Товар SET количество=5 WHERE id=4')
        order_id = orders.create_order('Клиент', [(4, None, 2, None)], current_user=self.actor)
        self.assertIsInstance(order_id, int)
        self.assertEqual(orders.get_product_quantity(4), 3)
        self.assertGreater(orders.get_order_total(order_id, current_user=self.actor), 0)

    def test_backup_is_a_valid_database(self):
        path = backup_db.backup_database()
        with closing(sqlite3.connect(path)) as connection:
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM Заказ').fetchone()[0], self.counts()[0])

class StockTests(DatabaseTests):

    def test_decrease_never_produces_negative_stock(self):
        self.execute('UPDATE Товар SET количество=1 WHERE id=1')
        self.assertFalse(orders.decrease_product_quantity(1, 5))
        self.assertEqual(orders.get_product_quantity(1), 1)
        self.assertTrue(orders.decrease_product_quantity(1, 1))
        self.assertEqual(orders.get_product_quantity(1), 0)
        self.assertFalse(orders.decrease_product_quantity(1, 1))

    def test_two_buyers_cannot_buy_same_last_unit(self):
        from concurrent.futures import ThreadPoolExecutor
        self.execute('UPDATE Товар SET количество=1 WHERE id=1')
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda client: orders.create_order(client, [(1, None, 1, 100)], current_user=self.actor), ['Клиент 1', 'Клиент 2']))
        self.assertEqual(sum((result is not None for result in results)), 1)
        self.assertEqual(orders.get_product_quantity(1), 0)

class ListTests(DatabaseTests):

    def test_orders_sorted_and_items_belong_to_selected_order(self):
        order_id = orders.create_order('Уникальный клиент', [(1, None, 1, 123)], current_user=self.actor)
        rows = orders.get_all_orders(current_user=self.actor)
        self.assertEqual(rows[0][0], order_id)
        self.assertEqual(rows[0][2], 'Уникальный клиент')
        items = orders.get_order_items(order_id, current_user=self.actor)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][4], 1)
        self.assertEqual(items[0][5], 123)

    def test_empty_composition_and_total(self):
        order_id = orders.add_order_to_db('Пустой учебный заголовок')
        self.assertEqual(orders.get_order_items(order_id, current_user=self.actor), [])
        self.assertEqual(orders.get_order_total(order_id, current_user=self.actor), Decimal('0.00'))

class JoinTests(DatabaseTests):

    def test_join_returns_real_name_and_developer(self):
        name, developer = self.rows('SELECT название, разработчик FROM Товар WHERE id=1')[0]
        order_id = orders.create_order('Клиент', [(1, None, 1, 100)], current_user=self.actor)
        item = orders.get_order_items(order_id, current_user=self.actor)[0]
        self.assertEqual(len(item), 6)
        self.assertEqual(item[1:3], (name, developer))
        self.assertIsNone(item[3])

    def test_total_equals_sum_of_joined_positions(self):
        order_id = orders.create_order('Клиент', [(1, None, 2, 10.1), (2, None, 3, 20.2)], current_user=self.actor)
        joined = orders.get_order_items(order_id, current_user=self.actor)
        total = sum((Decimal(str(item[5])) * item[4] for item in joined), Decimal('0.00'))
        self.assertEqual(orders.get_order_total(order_id, current_user=self.actor), total)
        self.assertEqual(total, Decimal('80.80'))
class RoleTests(DatabaseTests):
    def test_existing_logins_and_fio_are_preserved(self):
        import database
        client = database.get_user_by_login("client2")
        manager = database.get_user_by_login("manager1")
        self.assertEqual(client[1:4], ("Петрова", "Анна", "Сергеевна"))
        self.assertEqual(manager[1:4], ("Сидоров", "Пётр", "Алексеевич"))
        self.assertEqual(manager[5], "Менеджер")

    def test_login_is_parameterized(self):
        import database
        self.assertIsNone(database.get_user_by_login("' OR 1=1 --"))
        self.assertIsNone(database.get_user_by_login("unknown"))

    def test_client_cannot_read_all_orders(self):
        import database
        client = database.get_user_by_login("client1")
        self.assertIsNone(orders.get_all_orders(client))
        self.assertIsNone(orders.get_order_items(1, client))
        self.assertIsNotNone(orders.get_all_orders(self.actor))

    def test_guest_cannot_create_but_client_can(self):
        import database
        before = self.counts()
        self.assertIsNone(orders.create_order("Клиент", [(1, None, 1, 100)]))
        self.assertEqual(self.counts(), before)
        client = database.get_user_by_login("client1")
        self.assertIsInstance(orders.create_order("Клиент", [(1, None, 1, 100)], current_user=client), int)


class EditTests(DatabaseTests):
    def make_order(self):
        return orders.create_order("Клиент", [(1, None, 2, 100)], current_user=self.actor)

    def test_admin_changes_date(self):
        order_id = self.make_order()
        self.assertTrue(orders.update_order_date(order_id, "2024-02-29", self.actor))
        self.assertEqual(orders.get_order_by_id(order_id, self.actor)[1], "2024-02-29")

    def test_invalid_dates_are_rejected(self):
        order_id = self.make_order()
        before = orders.get_order_by_id(order_id, self.actor)
        for value in ("", "2024-02-30", "2024-2-1", "abc"):
            with self.subTest(value=value):
                self.assertFalse(orders.update_order_date(order_id, value, self.actor))
                self.assertEqual(orders.get_order_by_id(order_id, self.actor), before)

    def test_manager_cannot_edit(self):
        import database
        manager = database.get_user_by_login("manager1")
        order_id = self.make_order()
        item_id = orders.get_order_items(order_id, self.actor)[0][0]
        before = orders.get_product_quantity(1)
        self.assertFalse(orders.update_order_date(order_id, "2024-02-29", manager))
        self.assertFalse(orders.delete_order_item(item_id, manager))
        self.assertEqual(orders.get_product_quantity(1), before)

    def test_delete_returns_stock_exactly_once(self):
        before = orders.get_product_quantity(1)
        order_id = self.make_order()
        item_id = orders.get_order_items(order_id, self.actor)[0][0]
        self.assertEqual(orders.get_product_quantity(1), before-2)
        self.assertTrue(orders.delete_order_item(item_id, self.actor))
        self.assertEqual(orders.get_product_quantity(1), before)
        self.assertFalse(orders.delete_order_item(item_id, self.actor))
        self.assertEqual(orders.get_product_quantity(1), before)
        self.assertEqual(orders.get_order_total(order_id, self.actor), Decimal("0.00"))

    def test_failure_restoring_stock_rolls_back_delete(self):
        order_id = self.make_order()
        item_id = orders.get_order_items(order_id, self.actor)[0][0]
        before = orders.get_product_quantity(1)
        self.execute("CREATE TRIGGER test_fail_stock BEFORE UPDATE ON Товар BEGIN SELECT RAISE(ABORT, 'test'); END")
        self.assertFalse(orders.delete_order_item(item_id, self.actor))
        self.assertEqual(len(orders.get_order_items(order_id, self.actor)), 1)
        self.assertEqual(orders.get_product_quantity(1), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
