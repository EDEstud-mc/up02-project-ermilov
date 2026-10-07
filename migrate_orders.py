import sqlite3
from contextlib import closing

from backup_db import backup_database
from config import DB_PATH
from order_manager import get_connection


def migrate_orders():
    with closing(get_connection()) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(Заказ)")}
        if columns == {"id", "дата", "клиент"}:
            check = connection.execute("PRAGMA foreign_key_check").fetchall()
            if check:
                raise ValueError(f"Нарушены связи: {check}")
            return "Структура уже обновлена"
        if columns != {"id", "дата", "клиент", "товар_id", "количество"}:
            raise ValueError("Неожиданная структура Заказ: остановка без изменений")
    backup_path = backup_database()
    with closing(get_connection()) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        old = connection.execute("SELECT * FROM Заказ ORDER BY id").fetchall()
        missing = connection.execute(
            "SELECT Заказ.id FROM Заказ LEFT JOIN Товар ON Заказ.товар_id=Товар.id "
            "WHERE Товар.id IS NULL OR Заказ.количество <= 0 OR Товар.цена IS NULL"
        ).fetchall()
        if missing:
            raise ValueError(f"Некорректные старые заказы: {missing}")
        connection.execute("ALTER TABLE Заказ RENAME TO Заказ_старый")
        connection.execute("""
            CREATE TABLE Заказ (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                дата TEXT NOT NULL,
                клиент TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE Состав_заказа (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                заказ_id INTEGER NOT NULL,
                товар_id INTEGER NOT NULL,
                размер INTEGER,
                количество INTEGER NOT NULL CHECK(количество > 0),
                цена REAL NOT NULL CHECK(цена >= 0),
                FOREIGN KEY(заказ_id) REFERENCES Заказ(id) ON DELETE CASCADE,
                FOREIGN KEY(товар_id) REFERENCES Товар(id)
            )
        """)
        connection.execute(
            "INSERT INTO Заказ(id, дата, клиент) SELECT id, дата, клиент FROM Заказ_старый"
        )
        # Исторической цены в старой схеме нет: используем текущую базовую цену.
        connection.execute("""
            INSERT INTO Состав_заказа(заказ_id, товар_id, размер, количество, цена)
            SELECT Заказ_старый.id, товар_id, NULL, Заказ_старый.количество, Товар.цена
            FROM Заказ_старый JOIN Товар ON Заказ_старый.товар_id=Товар.id
        """)
        connection.execute("DROP TABLE Заказ_старый")
        if connection.execute("SELECT COUNT(*) FROM Состав_заказа").fetchone()[0] != len(old):
            raise ValueError("Количество перенесённых позиций не совпало")
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError(f"Нарушены внешние ключи: {violations}")
    return f"Перенесено {len(old)} заказов. Копия: {backup_path}"


if __name__ == "__main__":
    print(migrate_orders())
