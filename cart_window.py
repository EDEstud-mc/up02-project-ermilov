import tkinter as tk
from tkinter import ttk, messagebox

from catalog_data import format_price
from order_manager import create_order
from styles import COLOR_MAIN_BG, COLOR_ACCENT, font


class CartWindow:
    def __init__(self, parent, cart, on_saved=None, current_user=None):
        self.current_user = current_user
        self.cart = cart
        self.on_saved = on_saved
        self.window = tk.Toplevel(parent)
        self.window.title("Подтверждение заказа")
        self.window.geometry("750x450")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.client_var = tk.StringVar(self.window, value="")
        tk.Label(self.window, text="ФИО клиента:", bg=COLOR_MAIN_BG, font=font()).pack(anchor="w", padx=20)
        tk.Entry(self.window, textvariable=self.client_var, font=font()).pack(fill="x", padx=20, pady=8)
        self.tree = ttk.Treeview(self.window, columns=("name", "quantity", "price"), show="headings")
        for column, text in (("name", "Игра"), ("quantity", "Количество"), ("price", "Предварительная цена")):
            self.tree.heading(column, text=text)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        buttons = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons.pack(fill="x", padx=20, pady=10)
        for label, command in (("Удалить из корзины", self.remove_selected),
                               ("Подтвердить заказ", self.checkout),
                               ("Назад", self.window.destroy)):
            tk.Button(buttons, text=label, command=command, bg=COLOR_ACCENT,
                      fg="white", font=font()).pack(side="left", padx=5)
        self.load_items()

    def load_items(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product_id, item in self.cart.items():
            self.tree.insert("", "end", iid=str(product_id),
                             values=(item["name"], item["quantity"], format_price(item["price"])))

    def remove_selected(self):
        for selected in self.tree.selection():
            self.cart.pop(int(selected), None)
        self.load_items()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Корзина", "Добавьте игры в заказ", parent=self.window)
            return
        client = self.client_var.get().strip()
        if not client:
            messagebox.showwarning("Клиент", "Укажите ФИО клиента", parent=self.window)
            return
        items = [(product_id, None, item["quantity"], None)
                 for product_id, item in self.cart.items()]
        order_id = create_order(client, items, current_user=self.current_user)
        if order_id is None:
            return
        self.cart.clear()
        self.load_items()
        messagebox.showinfo("Успех", f"Заказ №{order_id} сохранён", parent=self.window)
        if self.on_saved is not None:
            from error_handler import safe_call
            safe_call(self.on_saved)
        self.window.destroy()
