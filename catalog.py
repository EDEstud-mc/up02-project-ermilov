"""Каталог товаров."""
import tkinter as tk
from tkinter import ttk
import os

from config import DB_PATH, FONT_FAMILY
import databases as db
from resources import get_product_image


def create_product_card(parent, product):
    """
    Создаёт карточку товара по макету с разделительной линией снизу.
    
    :param parent: родительский контейнер
    :param product: объект, кортеж или словарь из БД
    """
    # Универсальное и безопасное извлечение полей
    if isinstance(product, dict):
        p_id = product.get('id', '')
        genre = product.get('жанр', product.get('genre', ''))
        name = product.get('название', product.get('name', ''))
        developer = product.get('разработчик', product.get('developer', ''))
        price = product.get('цена', product.get('price', 0))
        qty = product.get('количество', product.get('quantity', product.get('qty', 0)))
        image_file = product.get('обложка', product.get('image', ''))
    elif hasattr(product, '__dict__') and not isinstance(product, (tuple, list)):
        p_id = getattr(product, 'id', '')
        genre = getattr(product, 'жанр', getattr(product, 'genre', ''))
        name = getattr(product, 'название', getattr(product, 'name', ''))
        developer = getattr(product, 'разработчик', getattr(product, 'developer', ''))
        price = getattr(product, 'цена', getattr(product, 'price', 0))
        qty = getattr(product, 'количество', getattr(product, 'quantity', getattr(product, 'qty', 0)))
        image_file = getattr(product, 'обложка', getattr(product, 'image', ''))
    else:
        # Если пришел кортеж, проверяем его длину, чтобы избежать IndexError
        # Приводим индексы к фактическому порядку полей вашей БД
        p_id = product[0] if len(product) > 0 else ''
        name = product[1] if len(product) > 1 else ''       # Например: GTA V
        developer = product[2] if len(product) > 2 else ''  # Например: Rockstar
        genre = product[3] if len(product) > 3 else ''      # Например: Экшен
        price = product[4] if len(product) > 4 else 0
        qty = product[5] if len(product) > 5 else 0
        
        # Если картинок в кортеже нет или индекс другой — проверяем 6-й элемент
        image_file = product[6] if len(product) > 6 else ''
        
        # Автоподбор имени картинки по названию игры, если поле обложки пустое
        if not image_file and name:
            # Убираем пробелы и спецсимволы для поиска (gta_v.png, fifa_24.png и т.д.)
            clean_name = str(name).lower().replace(" ", "_").replace("|", "")
            image_file = f"{clean_name}.png"

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
    
    # Получаем PhotoImage из модуля ресурсов
    photo = get_product_image(image_file, size=(100, 100))
    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo   # СОХРАНЯЕМ ССЫЛКУ!
        img_label.pack()
    else:
        tk.Label(img_frame, text="[НЕТ ФОТО]", bg=bg_color,
                 width=10, height=5).pack()

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
    """Создаёт главное окно каталога с шапкой и логотипом."""
    root = tk.Tk()
    root.title("Каталог товаров")
    root.geometry("700x600")

    header = tk.Frame(root, bg="#D2F6E7", height=60)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)

    logo_photo = get_product_image("logo.png", size=(50, 50))
    if logo_photo:
        lbl_logo = tk.Label(header, image=logo_photo, bg="#D2F6E7")
        lbl_logo.image = logo_photo
        lbl_logo.pack(side="left", padx=10, pady=5)
    else:
        tk.Label(header, text="[LOGO]", font=(FONT_FAMILY, 10, "bold"), bg="#D2F6E7").pack(side="left", padx=10)

    tk.Label(header, text="Каталог игр", font=(FONT_FAMILY, 16, "bold"), bg="#D2F6E7", fg="#2C3E50").pack(side="left", padx=5)

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(fill="both", expand=True)

    test_data = [
        (1, "Ведьмак 3", "CD Projekt", "RPG", 1500, 10, "witcher.png"),  
        (2, "Civilization VI", "Firaxis", "Стратегия", 1200, 2, ""),     
        (3, "Minecraft", "Mojang", "Песочница", 2000, 0, "mine.png")     
    ]

    for prod in test_data:
        create_product_card(main_frame, prod)

    root.mainloop()


if __name__ == "__main__":
    create_catalog_window()
