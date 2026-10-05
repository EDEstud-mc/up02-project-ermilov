import argparse
from copy import copy
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch

from catalog import create_product_card, _get_card_color, _indicator
from catalog_data import prepare_product
from db_products import get_all_products
from styles import COLOR_MAIN_BG, FONT_SIZE_NORMAL, font


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extended", action="store_true", help="Добавить три случая ДЗ")
    args = parser.parse_args()
    products = get_all_products()
    if not products:
        raise SystemExit("В таблице Товар нет товаров")
    cases = [(f"Количество = {qty}", {"quantity": qty}) for qty in (0, 3, 4, 5, 6, 100)]
    cases.extend([
        ("Нет обложки — ожидается picture.png", {"cover": None}),
        ("Пустое название — [Без названия]", {"name": ""}),
        ("Цена = 0 — 0 руб.", {"price": 0}),
        ("Цена None — 0 руб.", {"price": None}),
        ("Кириллица", {"name": "Ведьмак 3 — Дикая Охота"}),
    ])
    if args.extended:
        cases.extend([
            ("ДЗ: название > 100 символов", {"name": "Очень длинное название видеоигры " * 5}),
            ("ДЗ: цена > миллиона", {"price": 1250000}),
            ("ДЗ: кириллица + латиница", {"name": "Ведьмак 3 — The Witcher 3: Wild Hunt"}),
        ])
    with tempfile.TemporaryDirectory() as directory:
        broken = Path(directory) / "broken.png"
        broken.write_bytes(b"not a valid PNG")
        cases.append(("Битая обложка — ожидается picture.png", {"cover": str(broken)}))
        root = tk.Tk()
        root.title("Пара 15 — отладка, вариант 27")
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
        for title, changes in cases:
            product = copy(products[0])
            for attribute, value in changes.items():
                setattr(product, attribute, value)
            data = prepare_product(product)
            print(f"[CARD] {title}: qty={data['quantity']}, "
                  f"bg={_get_card_color(data['quantity'])}, "
                  f"indicator={_indicator(data['quantity'])}")
            tk.Label(frame, text=title, bg=COLOR_MAIN_BG, font=font(bold=True)).pack(fill="x", padx=10, pady=(10, 0))
            create_product_card(frame, product)
        tk.Label(frame, text="Нет обложки и заглушки — ожидается [НЕТ ФОТО]",
                 bg=COLOR_MAIN_BG, font=font(bold=True)).pack(fill="x", padx=10, pady=(10, 0))
        # Только для этой карточки имитируем отказ загрузчика. Файлы не меняем.
        with patch("catalog.get_product_image", return_value=None):
            create_product_card(frame, copy(products[0]))
        root.mainloop()


if __name__ == "__main__":
    main()
