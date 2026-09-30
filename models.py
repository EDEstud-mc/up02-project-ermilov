"""Модели данных для проекта УП.02."""


class Product:
    """Класс Товар (Игра)."""

    def __init__(self, product_id, genre, name, developer, price, quantity, cover):
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

    def is_available(self):
        """Проверка наличия товара на складе."""
        return self.quantity > 0

    def info(self):
        """Строка с информацией о товаре."""
        return (
            f"Игра: {self.name} ({self.genre}) от {self.developer} | "
            f"Цена: {self.price} руб. × {self.quantity} шт. = {self.total()} руб. "
            f"({self.indicator()})"
        )


class Order:
    """Класс Заказ."""

    def __init__(self, order_id, date, client, product, quantity):
        """
        Инициализация заказа.
        
        :param order_id: id заказа
        :param date: дата заказа
        :param client: ФИО клиента
        :param product: ОБЪЕКТ класса Product
        :param quantity: количество заказанного товара
        """
        self.id = order_id
        self.date = date
        self.client = client
        self.product = product      # Сюда передаем объект Product целиком
        self.quantity = quantity

    def total(self):
        """Стоимость конкретного заказа."""
        return self.product.price * self.quantity

    def info(self):
        """Строка с информацией о заказе."""
        return (
            f"Заказ №{self.id} от {self.date} | Клиент: {self.client} | "
            f"Товар: «{self.product.name}» × {self.quantity} шт. | "
            f"Сумма заказа: {self.total()} руб."
        )
