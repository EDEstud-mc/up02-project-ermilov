"""Главное окно приложения с каталогом."""
import os
import tkinter as tk
from tkinter import ttk
from config import APP_TITLE, FONT_FAMILY
import db_products as db  # Исправленный импорт
from catalog import create_product_card
from resources import load_image_proportional, PATH_ICON  # Добавленные импорты


def set_app_icon(root, icon_path):
    """Устанавливает иконку приложения кроссплатформенно с защитой от ошибок путей."""
    import os
    from resources import load_image_proportional

    # Превращаем путь в абсолютный, чтобы Tkinter всегда находил файл из любой директории
    abs_icon_path = os.path.abspath(icon_path)

    try:
        if os.name == "nt":   # Windows
            if os.path.exists(abs_icon_path):
                try:
                    root.iconbitmap(abs_icon_path)
                except Exception:
                    # Резервный вариант, если .ico файл поврежден или имеет неверный формат
                    png_path = abs_icon_path.replace(".ico", ".png")
                    icon_img = load_image_proportional(png_path, max_size=(32, 32))
                    if icon_img:
                        root.iconphoto(True, icon_img)
                        root._icon_photo = icon_img
        else:                  # Linux/Mac
            png_path = abs_icon_path.replace(".ico", ".png")
            icon_img = load_image_proportional(png_path, max_size=(32, 32))
            if icon_img:
                root.iconphoto(True, icon_img)
                root._icon_photo = icon_img   # сохраняем ссылку
    except Exception as e:
        print(f"Не удалось установить иконку: {e}")


class CatalogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")
        self.root.minsize(600, 500)

        # 6.2. Установка иконки кроссплатформенно
        set_app_icon(self.root, PATH_ICON)

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
        
        # Создаем окно внутри Canvas для размещения фрейма с карточками
        self.canvas_window = self.canvas.create_window((0, 0), window=self.catalog_frame, anchor="nw")
        
        # Автоматическое растягивание содержимого по ширине Canvas
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка Canvas и Scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязка прокрутки колесиком мыши (кроссплатформенная)
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows/macOS
        self.root.bind_all("<Button-4>", self.on_mousewheel)    # Linux
        self.root.bind_all("<Button-5>", self.on_mousewheel)    # Linux

    def on_canvas_configure(self, event):
        """Обновляет ширину внутреннего фрейма при изменении размеров Canvas."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        """Обработка прокрутки колесиком мыши."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_products(self):
        """Загрузка списка товаров из базы данных."""
        products = db.get_all_products()
        
        # Карточки упаковываются вертикально через .pack(), как заложено в catalog.py
        for p in products:
            create_product_card(self.catalog_frame, p)

    def run(self):
        """Запуск главного цикла приложения."""
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()
