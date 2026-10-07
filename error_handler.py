import sqlite3
from tkinter import messagebox


def safe_call(func, *args, **kwargs):
    """Возвращает результат функции; при ошибке сообщает о ней и возвращает None."""
    try:
        return func(*args, **kwargs)
    except FileNotFoundError as error:
        messagebox.showerror("Ошибка файла", f"Файл не найден:\n{error}")
    except ConnectionError as error:
        messagebox.showerror("Ошибка соединения", str(error))
    except sqlite3.Error as error:
        messagebox.showerror("Ошибка БД", f"Не удалось выполнить запрос:\n{error}")
    except ValueError as error:
        messagebox.showwarning("Некорректные данные", str(error))
    except Exception as error:
        messagebox.showerror("Ошибка", f"Операция не выполнена:\n{error}")
    return None


def validate_positive_int(value, field_name="Значение"):
    """Проверяет строку из Entry, не выполняя никаких запросов к БД."""
    try:
        number = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} должно быть целым числом"
    if number <= 0:
        return False, f"{field_name} должно быть больше нуля"
    return True, number
