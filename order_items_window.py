import tkinter as tk
from tkinter import ttk, messagebox

import order_manager as orders
from catalog_data import format_price
from error_handler import safe_call
from permissions import require_order_view, is_admin
from styles import COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, font


class OrderItemsWindow:
    def __init__(self, parent, order_id, current_user=None, on_changed=None):
        require_order_view(current_user)
        self.order_id = order_id
        self.current_user = current_user
        self.on_changed = on_changed
        self.window = tk.Toplevel(parent)
        self.window.title(f"Состав заказа №{order_id}")
        self.window.geometry("1000x620")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.build_ui()
        self.refresh_all()

    def is_admin(self):
        return is_admin(self.current_user)

    def build_ui(self):
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG)
        header.pack(fill="x")
        tk.Label(header, text=f"СОСТАВ ЗАКАЗА №{self.order_id}", bg=COLOR_SECONDARY_BG,
                 font=font(18, bold=True)).pack(pady=15)
        info = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        info.pack(fill="x", padx=20, pady=10)
        tk.Label(info, text="Дата:", bg=COLOR_MAIN_BG, font=font()).pack(side="left")
        self.date_var = tk.StringVar(self.window, value="")
        tk.Entry(info, textvariable=self.date_var, width=12, font=font(),
                 state="normal" if self.is_admin() else "readonly").pack(side="left", padx=5)
        if self.is_admin():
            tk.Button(info, text="Сохранить дату", command=self.save_date,
                      bg=COLOR_ACCENT, fg="white", font=font()).pack(side="left", padx=5)
        self.client_label = tk.Label(info, text="", bg=COLOR_MAIN_BG, font=font())
        self.client_label.pack(side="right")
        body = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        body.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("id", "name", "developer", "size", "quantity", "price", "total")
        self.tree = ttk.Treeview(body, columns=columns, show="headings")
        headings = (("id", "№", 50), ("name", "Игра", 230), ("developer", "Разработчик", 160),
                    ("size", "Размер", 100), ("quantity", "Количество", 90),
                    ("price", "Цена", 120), ("total", "Сумма", 140))
        for column, title, width in headings:
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, minwidth=width, stretch=False)
        vertical = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(body, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        horizontal.pack(side="bottom", fill="x")
        vertical.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.total_label = tk.Label(self.window, text="", bg=COLOR_MAIN_BG, font=font(bold=True))
        self.total_label.pack(pady=5)
        buttons = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons.pack(fill="x", padx=20, pady=10)
        if self.is_admin():
            tk.Button(buttons, text="Удалить позицию", command=self.delete_item,
                      bg=COLOR_ACCENT, fg="white", font=font()).pack(side="left", padx=5)
        for text, command in (("Обновить", self.refresh_all), ("Назад", self.window.destroy)):
            tk.Button(buttons, text=text, command=command, bg=COLOR_ACCENT,
                      fg="white", font=font()).pack(side="left", padx=5)

    def load_order_info(self):
        order = orders.get_order_by_id(self.order_id, self.current_user)
        if order is not None:
            self.date_var.set(order[1])
            self.client_label.configure(text=f"Клиент: {order[2]}")

    def load_items(self):
        rows = orders.get_order_items(self.order_id, self.current_user)
        if rows is None:
            self.total_label.configure(text="Не удалось прочитать состав")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item_id, name, developer, size, quantity, price in rows:
            amount = orders._money(price)
            self.tree.insert("", "end", iid=str(item_id),
                             values=(item_id, name, developer, "Не применим", quantity,
                                     format_price(amount), format_price(amount*quantity)))
        total = orders.get_order_total(self.order_id, self.current_user)
        self.total_label.configure(text=(f"ИТОГО: {format_price(total)} руб."
                                         if total is not None else "Не удалось рассчитать итог"))

    def refresh_all(self):
        self.load_order_info()
        self.load_items()

    def notify_change(self):
        self.refresh_all()
        if self.on_changed is not None:
            safe_call(self.on_changed)

    def save_date(self):
        if not self.is_admin():
            messagebox.showerror("Доступ", "Только для Администратора", parent=self.window)
            return
        new_date = self.date_var.get().strip()
        if orders.update_order_date(self.order_id, new_date, self.current_user):
            messagebox.showinfo("Успех", "Дата обновлена", parent=self.window)
            self.notify_change()

    def delete_item(self):
        if not self.is_admin():
            messagebox.showerror("Доступ", "Только для Администратора", parent=self.window)
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Позиция", "Выберите позицию", parent=self.window)
            return
        item_id = int(selected[0])
        if not messagebox.askyesno("Подтверждение", f"Удалить позицию №{item_id} и вернуть товар на склад?",
                                  parent=self.window):
            return
        if orders.delete_order_item(item_id, self.current_user):
            messagebox.showinfo("Успех", "Позиция удалена, остаток восстановлен", parent=self.window)
            self.notify_change()
