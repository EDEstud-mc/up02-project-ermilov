import tkinter as tk
from tkinter import ttk, messagebox

import order_manager as orders
from error_handler import safe_call
from permissions import require_order_view
from styles import COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, font


class OrdersWindow:
    def __init__(self, parent, current_user=None, on_changed=None):
        require_order_view(current_user)
        self.current_user = current_user
        self.on_changed = on_changed
        self.window = tk.Toplevel(parent)
        self.window.title("Список заказов")
        self.window.geometry("850x520")
        self.window.configure(bg=COLOR_MAIN_BG)
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG)
        header.pack(fill="x")
        tk.Label(header, text="СПИСОК ЗАКАЗОВ", bg=COLOR_SECONDARY_BG,
                 font=font(18, bold=True)).pack(pady=15)
        body = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        body.pack(fill="both", expand=True, padx=20, pady=15)
        self.tree = ttk.Treeview(body, columns=("id", "date", "client"), show="headings")
        for column, title, width in (("id", "№", 60), ("date", "Дата", 140), ("client", "ФИО клиента", 500)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.on_order_select)
        buttons = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons.pack(fill="x", padx=20, pady=10)
        for text, command in (("Просмотр состава", self.on_order_select),
                              ("Обновить", self.load_orders), ("Назад", self.window.destroy)):
            tk.Button(buttons, text=text, command=command, bg=COLOR_ACCENT,
                      fg="white", font=font()).pack(side="left", padx=5)
        self.load_orders()

    def load_orders(self):
        rows = orders.get_all_orders(self.current_user)
        if rows is None:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for order_id, date, client in rows:
            self.tree.insert("", "end", iid=str(order_id), values=(order_id, date, client))

    def on_order_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Заказы", "Выберите заказ", parent=self.window)
            return
        order_id = int(selected[0])
        from order_items_window import OrderItemsWindow
        safe_call(OrderItemsWindow, self.window, order_id, self.current_user, self.refresh_after_change)

    def refresh_after_change(self):
        self.load_orders()
        if self.on_changed is not None:
            safe_call(self.on_changed)
