import tkinter as tk
from tkinter import ttk
from decimal import Decimal

import order_manager as orders
from catalog_data import format_price
from permissions import require_order_view
from styles import COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, font


class OrderItemsWindow:
    def __init__(self, parent, order_id, current_user=None, on_changed=None):
        require_order_view(current_user)
        self.order_id = order_id
        self.current_user = current_user
        self.on_changed = on_changed
        self.window = tk.Toplevel(parent)
        self.window.title(f"Состав заказа №{order_id}")
        self.window.geometry("850x500")
        self.window.configure(bg=COLOR_MAIN_BG)
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG)
        header.pack(fill="x")
        tk.Label(header, text=f"СОСТАВ ЗАКАЗА №{order_id}", bg=COLOR_SECONDARY_BG,
                 font=font(18, bold=True)).pack(pady=15)
        body = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        body.pack(fill="both", expand=True, padx=20, pady=15)
        columns = ("name", "developer", "size", "quantity", "price", "total")
        self.tree = ttk.Treeview(body, columns=columns, show="headings")
        for column, title, width in (("name", "Игра", 230), ("developer", "Разработчик", 150), ("size", "Размер", 80),
                                     ("quantity", "Количество", 100), ("price", "Цена", 120),
                                     ("total", "Сумма", 120)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.total_label = tk.Label(self.window, text="", bg=COLOR_MAIN_BG, font=font(bold=True))
        self.total_label.pack(pady=5)
        buttons = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons.pack(fill="x", padx=20, pady=10)
        for title, command in (("Обновить", self.load_items), ("Назад", self.window.destroy)):
            tk.Button(buttons, text=title, command=command, bg=COLOR_ACCENT,
                      fg="white", font=font()).pack(side="left", padx=5)
        self.load_items()

    def load_items(self):
        rows = orders.get_order_items(self.order_id, self.current_user)
        if rows is None:
            self.total_label.configure(text="Не удалось прочитать состав")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        total = Decimal("0.00")
        for item_id, name, developer, size, quantity, price in rows:
            amount = Decimal(str(price))
            total += amount * quantity
            self.tree.insert("", "end", iid=str(item_id),
                             values=(name, developer, "Не применим", quantity,
                                     format_price(amount), format_price(amount*quantity)))
        stored_total = orders.get_order_total(self.order_id, self.current_user)
        if stored_total is None:
            self.total_label.configure(text="Не удалось рассчитать итог")
            return
        self.total_label.configure(text=f"ИТОГО: {format_price(stored_total)} руб.")
