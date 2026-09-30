"""Модели данных для проекта УП.02."""
from datetime import datetime
from discount import calculate_price_with_discount


class Product:
    """Класс Товар."""

    # Адаптировано под Вариант 27: id, название, жанр, цена, количество, разработчик, обложка
    def __init__(self, product_id, name, genre, price, quantity, developer=None, cover=None):
        self.id = product_id
        self.name = name
        self.genre = genre  # вместо category
        self.price = price
        self.quantity = quantity
        self.developer = developer
        self.cover = cover

    def total(self):
        return self.price * self.quantity

    def price_with_discount_auto(self, date=None):
        """Цена со скидкой по алгоритму ДЭ."""
        if date is None:
            date = datetime.now()
        return calculate_price_with_discount(self.id, self.price, date)

    def indicator(self):
        return "много" if self.quantity > 5 else "мало"

    def info(self):
        return (
            f"{self.name} ({self.genre}): "
            f"{self.price} руб. × {self.quantity} = {self.total()} руб. "
            f"({self.indicator()})"
        )
        
    def discounted_price(self):
        return self.price * 0.90 

