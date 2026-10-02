"""Главное окно приложения с каталогом."""
import tkinter as tk
from tkinter import ttk
from config import APP_TITLE, FONT_FAMILY
import db_products as db  # Исправленный импорт
from catalog import create_product_card


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")

        self.build_ui()
        self.load_products()

    def build_ui(self):
        # Заголовок
        header = tk.Frame(self.root, bg="#D2F6E7")
        header.pack(fill="x")
        tk.Label(header, text="КАТАЛОГ ТОВАРОВ",
                 font=(FONT_FAMILY, 16, "bold"),
                 bg="#D2F6E7").pack(pady=15)

        # Область с прокруткой
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical",
                                   command=self.canvas.yview)
        self.catalog_frame = tk.Frame(self.canvas, bg="white")
        self.catalog_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.catalog_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_products(self):
        products = db.get_all_products()
        for p in products:
            create_product_card(self.catalog_frame, p)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()
