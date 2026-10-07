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
from resources import load_image_proportional, PATH_LOGO, PATH_ICON
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG,
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
        self.order_items = {}
        self.build_ui()
        self.load_products()

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
        ).pack(expand=True)

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
                self.catalog_frame, product, on_add_to_order=self.add_to_order
            )
        except (ValueError, TypeError, AttributeError, IndexError) as error:
            errors.append(f"id={getattr(product, 'id', '?')}: {error}")

    def add_to_order(self, product, quantity=1):
        """Учебный заказ в памяти. Записи в SQLite эта пара не создаёт."""
        data = prepare_product(product)
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Количество должно быть положительным целым числом")
        current = self.order_items.get(data["id"], 0)
        if current + quantity > data["quantity"]:
            available = max(0, data["quantity"] - current)
            raise ValueError(f"Можно добавить ещё {available} шт.")
        self.order_items[data["id"]] = current + quantity

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()
