"""Модели данных для проекта УП.02."""


class Product:
    """Класс Товар (Игра)."""

    def __init__(self, product_id, genre, name, developer, price, quantity, cover):
        """
        Инициализация товара на основе структуры вашей БД.

        :param product_id: идентификатор (id)
        :param genre: жанр игры (жанр)
        :param name: название игры (название)
        :param developer: компания-разработчик (разрабо...)
        :param price: цена в рублях (цена)
        :param quantity: остаток на складе (количес...)
        :param cover: имя файла изображения обложки (обложка)
        """
        self.id = product_id
        self.genre = genre
        self.name = name
        self.developer = developer
        self.price = price
        self.quantity = quantity
        self.cover = cover

    def total(self):
        """Общая стоимость (цена × количество)."""
        return self.price * self.quantity

    def price_with_discount(self, discount_percent):
        """Цена со скидкой."""
        return self.price * (1 - discount_percent / 100)

    def indicator(self):
        """Индикатор «много/мало» (порог 5)."""
        return "много" if self.quantity > 5 else "мало"

    def info(self):
        """Строка с информацией о товаре."""
        return (
            f"Игра: {self.name} ({self.genre}) от {self.developer} | "
            f"Цена: {self.price} руб. × {self.quantity} шт. = {self.total()} руб. "
            f"({self.indicator()}) | Обложка: {self.cover}"
        )
