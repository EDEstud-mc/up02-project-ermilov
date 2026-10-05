import tkinter as tk
from tkinter import ttk

from catalog import create_product_card
from check_highlight_db import read_products
from styles import COLOR_MAIN_BG, FONT_SIZE_NORMAL, font


def check_card_background(widget, expected):
    """Проверяет фон карточки, вложенных фреймов и меток рекурсивно."""
    errors = []
    if isinstance(widget, (tk.Frame, tk.Label)):
        actual = widget.cget("bg")
        if actual.lower() != expected.lower():
            errors.append(f"{widget.winfo_class()}: {actual}, ожидалось {expected}")
    for child in widget.winfo_children():
        errors.extend(check_card_background(child, expected))
    return errors


def main():
    products = read_products()
    if not products:
        raise SystemExit("В таблице Товар нет товаров")
    root = tk.Tk()
    root.title("Пара 14 — подсветка, вариант 27")
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
    cases = ((0, "#ff8080"), (2, "#ff8080"), (3, "#ff8080"),
             (4, "#FFFFFF"), (10, "#FFFFFF"))
    passed = 0
    for qty, expected in cases:
        tk.Label(frame, text=f"Копия GTA V: {qty} шт.; ожидается {expected}",
                 bg=COLOR_MAIN_BG, fg="#000000", font=font(bold=True)).pack(
                     fill="x", padx=10, pady=(10, 0))
        product = list(products[0])
        product[5] = qty
        card = create_product_card(frame, product)
        errors = check_card_background(card, expected)
        passed += int(not errors)
        print(f"{'FAIL' if errors else 'OK'} qty={qty}: фон всех фреймов и меток")
        for error in errors:
            print("  ", error)
    print(f"Фон карточек: {passed} / {len(cases)}")
    if passed != len(cases):
        root.destroy()
        raise AssertionError("Фон вложенных элементов отличается")
    root.mainloop()


if __name__ == "__main__":
    main()

