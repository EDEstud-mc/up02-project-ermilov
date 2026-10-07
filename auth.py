import tkinter as tk
from tkinter import messagebox

from database import get_user_by_login
from styles import COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, font


class AuthWindow:
    def __init__(self, parent, on_success):
        self.on_success = on_success
        self.window = tk.Toplevel(parent)
        self.window.title("Вход в систему")
        self.window.geometry("430x300")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)
        self.window.grab_set()
        tk.Label(self.window, text="ВХОД ПО ЛОГИНУ", bg=COLOR_SECONDARY_BG,
                 font=font(18, bold=True)).pack(fill="x", pady=(0, 20))
        self.login_var = tk.StringVar(self.window, value="")
        tk.Label(self.window, text="Логин:", bg=COLOR_MAIN_BG, font=font()).pack()
        entry = tk.Entry(self.window, textvariable=self.login_var, font=font())
        entry.pack(pady=10)
        entry.focus_set()
        entry.bind("<Return>", lambda event: self.login())
        tk.Button(self.window, text="Войти", command=self.login,
                  bg=COLOR_ACCENT, fg="white", font=font()).pack(pady=10)
        tk.Label(self.window, text="client1 / client2 / manager1 / admin1",
                 bg=COLOR_MAIN_BG, font=font(10)).pack()

    def login(self):
        login = self.login_var.get().strip()
        if not login:
            messagebox.showwarning("Вход", "Введите логин", parent=self.window)
            return
        user = get_user_by_login(login)
        if user is None:
            messagebox.showerror("Вход", "Не удалось войти. Проверьте логин и доступность БД.",
                                 parent=self.window)
            return
        self.window.destroy()
        self.on_success(user)
