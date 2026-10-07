from contextlib import closing

from order_manager import get_connection
from error_handler import safe_call


def _get_user_by_login(login):
    with closing(get_connection()) as connection:
        return connection.execute("""
            SELECT Пользователь.id, фамилия, имя, отчество, логин, Роль.название
            FROM Пользователь JOIN Роль ON Пользователь.роль_id=Роль.id
            WHERE логин=?
        """, (login.strip(),)).fetchone()


def get_user_by_login(login):
    return safe_call(_get_user_by_login, login)
