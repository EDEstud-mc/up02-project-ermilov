import os
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import db_products as db
from config import APP_TITLE, DB_PATH
from catalog import create_product_card
from catalog_data import prepare_product
from error_handler import safe_call
from discount import calculate_price_with_discount
from order_manager import get_product_quantity
from permissions import can_order, can_view_orders, is_admin
from resources import load_image_proportional, PATH_LOGO, PATH_ICON
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
)


def set_app_icon(root, icon_path):
    """Устанавливает ICO на Windows или PNG как резервный вариант."""
    abs_icon_path = os.path.abspath(icon_path)
    try:
        if os.name == "nt" and os.path.exists(abs_icon_path):
            try:
                root.iconbitmap(abs_icon_path)
                return
            except tk.TclError:
                pass
        png_path = os.path.splitext(abs_icon_path)[0] + ".png"
        icon_img = load_image_proportional(png_path, max_size=(32, 32))
        if icon_img:
            root.iconphoto(True, icon_img)
            root._icon_photo = icon_img
    except (OSError, tk.TclError):
        pass


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.option_add("*Font", font(FONT_SIZE_NORMAL))
        self.root.configure(bg=COLOR_MAIN_BG)
        self.style = ttk.Style(self.root)
        self.style.configure("TButton", font=font(FONT_SIZE_NORMAL))
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        set_app_icon(self.root, PATH_ICON)
        self.current_user = None
        self.cart = {}
        self.build_ui()
        self.load_products()
        self.add_role_buttons()
        self.root.after(0, self.require_auth)

    def build_ui(self):
        header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Логотип загружается с сохранением пропорций.
        logo = load_image_proportional(PATH_LOGO, max_size=(60, 60))
        if logo:
            logo_label = tk.Label(header, image=logo, bg=COLOR_SECONDARY_BG)
            logo_label.image = logo
            logo_label.pack(side="left", padx=15, pady=10)
        else:
            tk.Label(header, text="[ЛОГОТИП]", bg=COLOR_SECONDARY_BG).pack(
                side="left", padx=15
            )

        tk.Label(
            header, text="КАТАЛОГ ТОВАРОВ",
            font=font(FONT_SIZE_TITLE, bold=True), bg=COLOR_SECONDARY_BG
        ).pack(side="left", expand=True)

        account = tk.Frame(header, bg=COLOR_SECONDARY_BG)
        account.pack(side="right", padx=10)
        self.user_label = tk.Label(account, text="Не авторизован", bg=COLOR_SECONDARY_BG, font=font(10))
        self.user_label.pack(anchor="e")
        self.role_buttons = tk.Frame(account, bg=COLOR_SECONDARY_BG)
        self.role_buttons.pack(anchor="e")

        self.canvas = tk.Canvas(self.root, bg=COLOR_MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview
        )
        self.catalog_frame = tk.Frame(self.canvas, bg=COLOR_MAIN_BG)
        self.catalog_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.catalog_frame, anchor="nw"
        )
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind_all("<Button-4>", self.on_mousewheel)
        self.root.bind_all("<Button-5>", self.on_mousewheel)

    def on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        elif event.delta:
            step = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(step, "units")

    def load_products(self):
        if not Path(DB_PATH).is_file():
            messagebox.showerror(
                "Ошибка БД", "Не найден файл databases/db_variant_27.db.",
                parent=self.root
            )
            return
        products = safe_call(db.get_all_products)
        if products is None:
            return
        if not products:
            tk.Label(self.catalog_frame, text="В каталоге пока нет товаров",
                     bg=COLOR_MAIN_BG, fg="#000000", font=font()).pack(pady=20)
            return
        errors = []
        for product in products:
            safe_call(self._create_card_checked, product, errors)
        if errors:
            messagebox.showwarning(
                "Некорректные данные", "Некоторые товары не показаны:\n"
                + "\n".join(errors), parent=self.root
            )

    def _create_card_checked(self, product, errors):
        try:
            return create_product_card(
                self.catalog_frame, product, on_add_to_order=self.add_to_cart
            )
        except (ValueError, TypeError, AttributeError, IndexError) as error:
            errors.append(f"id={getattr(product, 'id', '?')}: {error}")

    def add_to_cart(self, product, quantity):
        if not can_order(self.current_user):
            raise PermissionError("Для оформления заказа войдите в систему")
        data = prepare_product(product)
        current = get_product_quantity(data["id"])
        if current is None:
            raise ValueError("Не удалось прочитать остаток")
        previous = self.cart.get(data["id"], {}).get("quantity", 0)
        if quantity <= 0 or previous + quantity > current:
            raise ValueError(f"Можно добавить ещё {max(0, current-previous)} шт.")
        price = calculate_price_with_discount(data["id"], data["price"])
        if price is None:
            raise ValueError("Не удалось рассчитать цену")
        self.cart[data["id"]] = dict(name=data["name"], quantity=previous+quantity, price=price)

    def open_orders(self):
        from orders_window import OrdersWindow
        if not can_view_orders(self.current_user):
            messagebox.showwarning("Доступ", "Заказы доступны Менеджеру и Администратору")
            return
        safe_call(OrdersWindow, self.root, self.current_user, self.refresh_catalog)

    def open_cart(self):
        from cart_window import CartWindow
        if not can_order(self.current_user):
            messagebox.showwarning("Доступ", "Сначала войдите в систему")
            return
        safe_call(CartWindow, self.root, self.cart, self.refresh_catalog, self.current_user)

    def require_auth(self):
        from auth import AuthWindow
        safe_call(AuthWindow, self.root, self.on_auth_success)

    def on_auth_success(self, user):
        self.current_user = user
        self.cart.clear()
        fio = " ".join(part for part in user[1:4] if part)
        self.user_label.configure(text=f"{fio} ({user[5]})")
        self.add_role_buttons()

    def add_role_buttons(self):
        for widget in self.role_buttons.winfo_children():
            widget.destroy()
        actions = [("Войти", self.require_auth)] if self.current_user is None else [
            ("Корзина", self.open_cart), ("Выйти", self.logout)]
        if can_view_orders(self.current_user):
            actions.insert(0, ("Заказы", self.open_orders))
        if is_admin(self.current_user):
            actions.insert(0, ("Админ-панель", self.open_admin))
        for title, command in actions:
            tk.Button(self.role_buttons, text=title, command=command,
                      bg=COLOR_ACCENT, fg="white", font=font(10)).pack(side="left", padx=2)

    def open_admin(self):
        if not is_admin(self.current_user):
            messagebox.showwarning("Доступ", "Только для Администратора")
            return
        self.open_orders()

    def logout(self):
        self.current_user = None
        self.cart.clear()
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        self.user_label.configure(text="Не авторизован")
        self.add_role_buttons()
        self.require_auth()

    def refresh_catalog(self):
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()
        self.load_products()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()
