import tkinter as tk
from tkinter import ttk

from catalog import create_product_card
from check_indicator_db import read_products
from styles import COLOR_MAIN_BG, FONT_SIZE_NORMAL, font


def main():
    products = read_products()
    if not products:
        raise SystemExit("В таблице Товар нет товаров")
    root = tk.Tk()
    root.title("Пара 13 — проверка индикатора, вариант 27")
    root.geometry("1000x750")
    root.option_add("*Font", font(FONT_SIZE_NORMAL))
    root.configure(bg=COLOR_MAIN_BG)
    canvas = tk.Canvas(root, bg=COLOR_MAIN_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    frame = tk.Frame(canvas, bg=COLOR_MAIN_BG)
    window = canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda event: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda event: canvas.itemconfigure(
        window, width=event.width))
    for qty, expected in ((0, "мало"), (4, "мало"), (5, "мало"),
                          (6, "много"), (100, "много")):
        tk.Label(frame, text=f"Остаток {qty}. Ожидается: {expected}",
                 bg=COLOR_MAIN_BG, fg="#000000", font=font(bold=True)).pack(
                     fill="x", padx=10, pady=(10, 0))
        product = list(products[0])
        product[5] = qty
        create_product_card(frame, product)
    root.mainloop()


if __name__ == "__main__":
    main()

