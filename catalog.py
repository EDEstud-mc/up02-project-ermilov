"""Каталог товаров для варианта 27."""
import os
import tkinter as tk
import databases as db

from resources import get_product_image
from styles import (
    COLOR_MAIN_BG, COLOR_ACCENT, COLOR_HIGHLIGHT,
    FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_HEADER, font
)


def create_product_card(parent, product):
    """Создаёт карточку товара из объекта, словаря или строки БД."""
    if isinstance(product, dict):
        p_id = product.get("id", "")
        genre = product.get("жанр", product.get("genre", ""))
        name = product.get("название", product.get("name", ""))
        developer = product.get("разработчик", product.get("developer", ""))
        price = product.get("цена", product.get("price", 0))
        qty = product.get("количество", product.get("quantity", product.get("qty", 0)))
        image_file = product.get("обложка", product.get("cover", product.get("image", "")))
    elif isinstance(product, (tuple, list)):
        # Порядок полей таблицы Товар в БД варианта 27.
        p_id, genre, name, developer, price, qty, image_file = product
    else:
        p_id = product.id
        genre = product.genre
        name = product.name
        developer = product.developer
        price = product.price
        qty = product.quantity
        image_file = product.cover

    bg_color = COLOR_HIGHLIGHT if qty <= 3 else COLOR_MAIN_BG

    card_container = tk.Frame(parent, bg=bg_color)
    card_container.pack(fill="x", padx=10, pady=2)
    card = tk.Frame(card_container, bg=bg_color)
    card.pack(fill="x", padx=5, pady=5)

    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    image_path = image_file or ""
    if image_path and not os.path.isabs(image_path):
        if not os.path.dirname(image_path):
            image_path = os.path.join("resources", image_path)
    photo = get_product_image(image_path, size=(100, 100))

    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo
        img_label.pack()
    else:
        tk.Label(
            img_frame, text="[НЕТ ФОТО]", bg=bg_color,
            font=font(FONT_SIZE_NORMAL), width=10, height=5
        ).pack()

    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    tk.Label(
        text_frame, text=f"{developer or ''} | {name}",
        font=font(FONT_SIZE_HEADER, bold=True), bg=bg_color, anchor="w"
    ).pack(fill="x")
    tk.Label(
        text_frame, text=f"Категория: {genre}",
        font=font(FONT_SIZE_NORMAL), bg=bg_color, anchor="w"
    ).pack(fill="x")
    tk.Label(
        text_frame, text=f"Цена: {price} руб.",
        font=font(FONT_SIZE_NORMAL), bg=bg_color, anchor="w"
    ).pack(fill="x")
    tk.Label(
        text_frame, text=f"В наличии: {qty} шт.",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "italic"),
        bg=bg_color, anchor="w"
    ).pack(fill="x")

    action_frame = tk.Frame(card, bg=bg_color)
    action_frame.pack(side="right", padx=10, pady=10, fill="y")
    tk.Button(
        action_frame, text="В корзину",
        bg=COLOR_ACCENT, fg=COLOR_MAIN_BG,
        activebackground=COLOR_ACCENT, activeforeground=COLOR_MAIN_BG,
        font=font(FONT_SIZE_NORMAL), relief="flat", padx=15, pady=5,
        state="normal" if qty > 0 else "disabled",
        command=lambda: db.add_to_cart(p_id)
    ).pack(expand=True)

    tk.Frame(card_container, height=1, bg=COLOR_ACCENT).pack(
        fill="x", padx=5, pady=(5, 0)
    )
    return card_container


def create_catalog_window():
    """Открывает каталог с товарами из БД."""
    from main_catalog import CatalogWindow
    CatalogWindow().run()


if __name__ == "__main__":
    create_catalog_window()
