import tkinter as tk

from catalog_data import (
    prepare_product, is_low_stock, format_price, product_image_path
)
from resources import get_product_image
from styles import (
    COLOR_MAIN_BG, COLOR_HIGHLIGHT, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, font
)


def create_product_card(parent, product, on_add_to_cart=None):
    """Создаёт карточку из объекта Product или строки БД варианта 27."""
    data = prepare_product(product)
    background = _get_card_color(data["quantity"])
    card = tk.Frame(parent, bg=background, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=5)
    _add_image(card, data, background)
    _add_price(card, data, background, on_add_to_cart)
    _add_text_info(card, data, background)
    return card


def _get_card_color(quantity):
    return COLOR_HIGHLIGHT if is_low_stock(quantity) else COLOR_MAIN_BG


def _add_image(card, data, background):
    frame = tk.Frame(card, bg=background)
    frame.pack(side="left", padx=10, pady=10)
    path = product_image_path(data["cover"])
    photo = get_product_image(str(path) if path else "", size=(100, 100))
    if photo:
        label = tk.Label(frame, image=photo, bg=background)
        label.image = photo
        label.pack()
    else:
        _add_label(frame, "[НЕТ ФОТО]", background)


def _add_text_info(card, data, background):
    frame = tk.Frame(card, bg=background)
    frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    _add_label(frame, f"{data['developer']} | {data['name']}",
               background, bold=True, size=FONT_SIZE_HEADER)
    _add_label(frame, f"Категория (жанр): {data['genre']}", background)
    _add_label(frame, f"Количество: {_indicator(data['quantity'])} ({data['quantity']} шт.)",
               background)


def _add_price(card, data, background, on_add_to_cart):
    frame = tk.Frame(card, bg=background)
    frame.pack(side="right", padx=10, pady=10)
    _add_label(frame, f"{format_price(data['price'])} руб.", background,
               bold=True, size=FONT_SIZE_HEADER, align="e")
    # В проекте пока нет функции корзины. Без обработчика кнопка отключена.
    enabled = data["quantity"] > 0 and on_add_to_cart is not None
    tk.Button(
        frame, text="В корзину", bg=COLOR_ACCENT, fg=COLOR_MAIN_BG,
        activebackground=COLOR_ACCENT, font=font(), relief="flat",
        padx=15, pady=5, state="normal" if enabled else "disabled",
        command=(lambda: on_add_to_cart(data["id"])) if enabled else None
    ).pack(pady=(10, 0))


def _add_label(parent, text, background, bold=False,
               size=FONT_SIZE_NORMAL, align="w"):
    label = tk.Label(parent, text=text, font=font(size, bold=bold),
                     bg=background, fg="#000000", anchor=align,
                     justify="left", wraplength=300)
    label.pack(fill="x", pady=2)
    # Перенос сохраняет полное длинное название при изменении ширины окна.
    label.bind("<Configure>", lambda event: label.configure(
        wraplength=max(40, event.width - 8)))
    return label


def _indicator(qty):
    """Возвращает «много» при qty > 5, иначе «мало» (порог КИМ)."""
    return "много" if qty > 5 else "мало"


if __name__ == "__main__":
    from main_catalog import CatalogWindow
    CatalogWindow().run()
