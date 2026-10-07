import tkinter as tk
from tkinter import messagebox

from catalog_data import prepare_product, format_price, product_image_path
from discount import calculate_price_with_discount
from resources import get_product_image
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
)
from error_handler import validate_positive_int, safe_call
from order_manager import get_product_quantity


class ViewForm:
    def __init__(self, parent, product, on_add_to_order=None):
        self.product = product
        self.on_add_to_order = on_add_to_order
        self.data = prepare_product(product) if product is not None else None
        self.final_price = None
        if self.data is not None:
            self.final_price = calculate_price_with_discount(
                self.data["id"], self.data["price"]
            )
        self.window = tk.Toplevel(parent)
        name = self.data["name"] if self.data else "товар не выбран"
        self.window.title(f"Просмотр — {name}")
        self.window.geometry("850x680")
        self.window.minsize(780, 620)
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(parent)
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="КАРТОЧКА ИГРЫ", bg=COLOR_SECONDARY_BG,
                 font=font(FONT_SIZE_TITLE, bold=True)).pack(pady=15)

        main = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)
        image_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        image_frame.pack(side="left", anchor="n", padx=10)
        path = product_image_path(self.data["cover"]) if self.data else None
        photo = get_product_image(str(path) if path else "", size=(200, 200))
        if photo is not None:
            label = tk.Label(image_frame, image=photo, bg=COLOR_MAIN_BG)
            label.image = photo
            label.pack()
        else:
            tk.Label(image_frame, text="[НЕТ ФОТО]", bg=COLOR_MAIN_BG,
                     font=font()).pack()

        info = tk.Frame(main, bg=COLOR_MAIN_BG)
        info.pack(side="left", fill="both", expand=True, padx=15)
        data = self.data or {}
        price = (f"{format_price(self.final_price)} руб."
                 if self.final_price is not None else "Не удалось рассчитать")
        self._add_field(info, "Разработчик", data.get("developer", "—"))
        self._add_field(info, "Наименование", data.get("name", "—"))
        self._add_field(info, "Категория (жанр)", data.get("genre", "—"))
        self._add_field(info, "Состав", "Не применим к видеоиграм")
        self._add_field(info, "Цена со скидкой", price)
        self._add_field(info, "Размеры", "Не применимы к видеоиграм")
        if self.data:
            self._add_field(info, "Обычная цена",
                            f"{format_price(data['price'])} руб.")
            self._add_field(info, "В наличии", f"{data['quantity']} шт.")
        self._add_field(info, "Описание", "В БД варианта 27 не хранится")
        row = tk.Frame(info, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Количество:", font=font(bold=True), width=17,
                 anchor="w", bg=COLOR_MAIN_BG).pack(side="left")
        self.quantity_var = tk.StringVar(self.window, value="1")
        tk.Entry(row, textvariable=self.quantity_var, width=8,
                 font=font()).pack(side="left")
        tk.Label(info, text="Добавьте игры в корзину, затем подтвердите единый заказ.",
                 bg=COLOR_MAIN_BG, font=font(10), wraplength=330,
                 justify="left").pack(anchor="w", pady=10)

        buttons = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons.pack(fill="x", pady=15)
        tk.Button(buttons, text="Добавить в заказ", command=self.add_to_order,
                  bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="left", padx=20)
        tk.Button(buttons, text="Назад", command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="right", padx=20)

    def _add_field(self, parent, label, value):
        row = tk.Frame(parent, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=f"{label}:", font=font(bold=True), width=17,
                 anchor="w", bg=COLOR_MAIN_BG).pack(side="left", anchor="n")
        value_label = tk.Label(row, text=str(value), font=font(),
                               bg=COLOR_MAIN_BG, anchor="w", justify="left",
                               wraplength=300)
        value_label.pack(side="left", fill="x", expand=True)
        value_label.bind("<Configure>", lambda event: value_label.configure(
            wraplength=max(60, event.width - 8)))

    def add_to_order(self):
        if self.product is None:
            messagebox.showerror("Ошибка", "Товар не выбран", parent=self.window)
            return
        if self.final_price is None:
            messagebox.showerror("Ошибка", "Сначала устраните ошибку расчёта цены",
                                 parent=self.window)
            return
        valid, result = validate_positive_int(self.quantity_var.get(), "Количество")
        if not valid:
            messagebox.showwarning("Некорректное количество", result,
                                   parent=self.window)
            return
        current = get_product_quantity(self.data["id"])
        if current is None:
            return
        if result > current:
            messagebox.showwarning("Недостаточно товара", f"Доступно {current} шт.",
                                   parent=self.window)
            return
        if self.on_add_to_order is None:
            messagebox.showerror("Корзина", "Не передан обработчик корзины", parent=self.window)
            return
        try:
            self.on_add_to_order(self.product, result)
        except Exception as error:
            messagebox.showwarning("Корзина", str(error), parent=self.window)
            return
        messagebox.showinfo("Корзина", "Игра добавлена. Подтвердите заказ в корзине.",
                            parent=self.window)
        self.window.destroy()
