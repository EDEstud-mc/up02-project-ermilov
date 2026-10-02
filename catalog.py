"""Каталог товаров."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from config import DB_PATH, COLOR_HIGHLIGHT, FONT_FAMILY
import databases as db


def create_product_card(parent, product):
    """
    Создаёт карточку товара по макету.
    
    :param parent: родительский контейнер
    :param product: объект или кортеж из БД
    """
    # Автоматически определяем, передан объект класса или кортеж,
    # и извлекаем значения полей согласно структуре вашей БД
    if hasattr(product, '__dict__') or not isinstance(product, (tuple, list)):
        # Если передан объект (работает через свойства .имя_поля или .id)
        p_id = getattr(product, 'id', '')
        genre = getattr(product, 'жанр', getattr(product, 'genre', ''))
        name = getattr(product, 'название', getattr(product, 'name', ''))
        developer = getattr(product, 'разработчик', getattr(product, 'developer', ''))
        price = getattr(product, 'цена', getattr(product, 'price', 0))
        qty = getattr(product, 'количество', getattr(product, 'quantity', getattr(product, 'qty', 0)))
        image_file = getattr(product, 'обложка', getattr(product, 'image', ''))
    else:
        # Если из БД пришёл обычный кортеж (индексы строго по вашей таблице Товар)
        p_id = product[0]          # id
        genre = product[1]         # жанр
        name = product[2]          # название
        developer = product[3]     # разработчик
        price = product[4]         # цена
        qty = product[5]           # количество
        image_file = product[6]    # обложка

    # === Настройка фона ===
    # Подсветка, если количество товара на складе <= 3
    bg_color = COLOR_HIGHLIGHT if qty <= 3 else "white"

    # Основной контейнер карточки — рамка со всех сторон
    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=5)

    # === Блок изображения (слева) ===
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    # Корректно склеиваем путь к папке ресурсов вашего проекта
    file_name = image_file if image_file and str(image_file).strip() != "" else "picture.png"
    image_path = os.path.join("resources", file_name)
    
    if not os.path.exists(image_path):
        image_path = os.path.join("resources", "picture.png")
              
    
    try:
        img = Image.open(image_path).resize((100, 100))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo   # сохраняем ссылку, чтобы картинка не исчезала
        img_label.pack()
    except Exception:
        tk.Label(img_frame, text="[ФОТО]", bg=bg_color, width=10, height=5).pack()

    # === Блок текстовой информации (справа) ===
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Строка: Разработчик | Название игры
    title = f"{developer} | {name}"
    tk.Label(text_frame, text=title, font=(FONT_FAMILY, 14, "bold"),
             bg=bg_color, anchor="w").pack(fill="x")

    # Строка: Категория (Жанр)
    tk.Label(text_frame, text=f"Категория: {genre}",
             font=(FONT_FAMILY, 11), bg=bg_color, anchor="w").pack(fill="x")

    # Строка: Цена товара
    tk.Label(text_frame, text=f"Цена: {price} руб.",
             font=(FONT_FAMILY, 11), bg=bg_color, anchor="w").pack(fill="x")

    # Строка: Остаток на складе
    tk.Label(text_frame, text=f"В наличии: {qty} шт.",
             font=(FONT_FAMILY, 11, "italic"), bg=bg_color, anchor="w").pack(fill="x")
