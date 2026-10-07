from contextlib import closing

from backup_db import backup_database
from order_manager import get_connection


def migrate_users():
    with closing(get_connection()) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(Пользователь)")}
        if "роль_id" in columns:
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("Нарушены связи пользователей")
            return "Пользователи уже обновлены"
        if columns != {"id", "логин", "фио", "роль"}:
            raise ValueError("Неожиданная структура Пользователь")
    backup_path = backup_database()
    with closing(get_connection()) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        users = connection.execute("SELECT id, логин, фио, роль FROM Пользователь ORDER BY id").fetchall()
        known = ("Клиент", "Менеджер", "Администратор")
        if any(role not in known for _, _, _, role in users):
            raise ValueError("В исходной БД есть неизвестная роль")
        connection.execute("CREATE TABLE IF NOT EXISTS Роль (id INTEGER PRIMARY KEY, название TEXT NOT NULL UNIQUE)")
        for role in known:
            connection.execute("INSERT OR IGNORE INTO Роль(название) VALUES (?)", (role,))
        roles = dict(connection.execute("SELECT название, id FROM Роль"))
        connection.execute("ALTER TABLE Пользователь RENAME TO Пользователь_старый")
        connection.execute("""
            CREATE TABLE Пользователь (
                id INTEGER PRIMARY KEY,
                фамилия TEXT NOT NULL,
                имя TEXT NOT NULL,
                отчество TEXT,
                логин TEXT NOT NULL UNIQUE,
                роль_id INTEGER NOT NULL REFERENCES Роль(id)
            )
        """)
        for user_id, login, fio, role in users:
            name_parts = str(fio).strip().split(maxsplit=2)
            if len(name_parts) < 2:
                raise ValueError(f"Неполное ФИО пользователя {login}")
            surname, name = name_parts[:2]
            patronymic = name_parts[2] if len(name_parts) == 3 else ""
            connection.execute(
                "INSERT INTO Пользователь VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, surname, name, patronymic, login, roles[role])
            )
        connection.execute("DROP TABLE Пользователь_старый")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Нарушены внешние ключи")
    return f"Сохранено {len(users)} пользователей. Копия: {backup_path}"


if __name__ == "__main__":
    print(migrate_users())
