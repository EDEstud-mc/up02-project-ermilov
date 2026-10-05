"""Визуальная проверка крайних случаев на копиях реального товара."""
from copy import copy
import tkinter as tk
from tkinter import ttk

from db_products import get_all_products
from catalog import create_product_card
from styles import COLOR_MAIN_BG, FONT_SIZE_NORMAL, font

products = get_all_products()
if not products:
    raise SystemExit("В таблице Товар нет товаров")
root = tk.Tk()
root.title("Пара 12 — крайние случаи варианта 27")
root.geometry("1000x750")
root.option_add("*Font", font(FONT_SIZE_NORMAL))
canvas = tk.Canvas(root, bg=COLOR_MAIN_BG, highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
frame = tk.Frame(canvas, bg=COLOR_MAIN_BG)
window = canvas.create_window((0, 0), window=frame, anchor="nw")
frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))

cases = (
    ("Нет фото", {"cover": None}),
    ("Нулевая цена", {"price": 0}),
    ("Пустое название", {"name": ""}),
    ("Остаток 0", {"quantity": 0}),
    ("Остаток 3", {"quantity": 3}),
    ("Остаток 4", {"quantity": 4}),
    ("Остаток 5", {"quantity": 5}),
    ("Остаток 6", {"quantity": 6}),
    ("Дорогая игра", {"price": 1250000}),
    ("Длинное название", {"name": "Очень длинное название видеоигры " * 5}),
    ("Кириллица", {"name": "Ведьмак 3 — Дикая Охота"}),
)
for title, changes in cases:
    tk.Label(frame, text=title, bg=COLOR_MAIN_BG, font=font(bold=True)).pack(fill="x", padx=10)
    product = copy(products[0])
    for attribute, value in changes.items():
        setattr(product, attribute, value)
    create_product_card(frame, product)
root.mainloop()
