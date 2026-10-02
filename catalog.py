"""Каталог товаров."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

from config import DB_PATH, FONT_FAMILY
import databases as db


def create_product_card(parent, product):
    """
    Создаёт карточку товара по макету с разделительной линией снизу.
    
    :param parent: родительский контейнер
    :param product: объект или кортеж из БД
    """
    # Автоматически определяем, передан объект класса или кортеж,
    # и извлекаем значения полей согласно структуре вашей БД
    if hasattr(product, '__dict__') or not isinstance(product, (tuple, list)):
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

    # === [Задание 1] Настройка фона ===
    # При количестве <= 3 фон становится светло-красным (#ff8080)
    bg_color = "#ff8080" if qty <= 3 else "white"

    # Основной контейнер карточки (без рамки, чтобы разделитель смотрелся лучше)
    card_container = tk.Frame(parent, bg=bg_color)
    card_container.pack(fill="x", padx=10, pady=2)

    card = tk.Frame(card_container, bg=bg_color)
    card.pack(fill="x", padx=5, pady=5)

    # === Блок изображения (слева) ===
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    # Корректно склеиваем путь к папке ресурсов вашего проекта
    file_name = image_file if image_file and str(image_file).strip() != "" else "picture.png"
    image_path = os.path.join("resources", file_name)
    
    if not os.path.exists(image_path):
        image_path = os.path.join("resources", "picture.png")
              
    try:
        img = Image.open(image_path).resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo   # сохраняем ссылку, чтобы картинка не исчезала
        img_label.pack()
    except Exception:
        tk.Label(img_frame, text="[ФОТО]", bg=bg_color, width=10, height=5).pack()

    # === Блок текстовой информации (по центру) ===
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
    qty_color = "#B71C1C" if qty <= 3 else "black"  # Темно-красный для читаемости на красном фоне
    tk.Label(text_frame, text=f"В наличии: {qty} шт.",
             font=(FONT_FAMILY, 11, "italic"), fg=qty_color, bg=bg_color, anchor="w").pack(fill="x")

    # === Блок кнопки действия (справа) ===
    action_frame = tk.Frame(card, bg=bg_color)
    action_frame.pack(side="right", padx=10, pady=10, fill="y")
    
    btn_state = "normal" if qty > 0 else "disabled"
    btn_buy = ttk.Button(
        action_frame, 
        text="В корзину", 
        state=btn_state,
        command=lambda: db.add_to_cart(p_id)
    )
    btn_buy.pack(expand=True)

    # === [Задание 1] Разделитель между карточками ===
    separator = tk.Frame(card_container, height=1, bg="#CCCCCC")
    separator.pack(fill="x", padx=5, pady=(5, 0))

    return card_container


def create_catalog_window():
    """
    Создаёт главное окно каталога с шапкой и логотипом.
    """
    root = tk.Tk()
    root.title("Каталог товаров")
    root.geometry("700x600")

    # === [Задание 2] Добавление логотипа в шапку ===
    header = tk.Frame(root, bg="#D2F6E7", height=60)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)

    try:
        logo = Image.open("resources/logo.png").resize((50, 50), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo)
        lbl_logo = tk.Label(header, image=logo_photo, bg="#D2F6E7")
        lbl_logo.image = logo_photo  # сохраняем ссылку
        lbl_logo.pack(side="left", padx=10, pady=5)
    except Exception:
        tk.Label(header, text="[LOGO]", font=(FONT_FAMILY, 10, "bold"), bg="#D2F6E7").pack(side="left", padx=10)

    tk.Label(header, text="Каталог игр", font=(FONT_FAMILY, 16, "bold"), bg="#D2F6E7", fg="#2C3E50").pack(side="left", padx=5)

    # Главная область для списка товаров
    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(fill="both", expand=True)

    # Тестовые данные для мгновенной проверки
    test_data = [
        (1, "RPG", "Ведьмак 3", "CD Projekt", 1500, 10, "witcher.png"),  # Нормальный фон
        (2, "Стратегия", "Civilization VI", "Firaxis", 1200, 2, ""),     # Будет фон #ff8080
        (3, "Песочница", "Minecraft", "Mojang", 2000, 0, "mine.png")     # Будет фон #ff8080, кнопка выключена
    ]

    for prod in test_data:
        create_product_card(main_frame, prod)

    root.mainloop()


if __name__ == "__main__":
    create_catalog_window()
