"""Подготовка полей карточки для варианта 27 без зависимости от Tkinter."""
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ("id", "жанр", "название", "разработчик", "цена", "количество", "обложка")
ATTRIBUTES = ("id", "genre", "name", "developer", "price", "quantity", "cover")
BASE_DIR = Path(__file__).resolve().parent


def _text(value, fallback):
    text = "" if value is None else str(value).strip()
    return text or fallback


def prepare_product(product):
    """Приводит Product, словарь или строку БД к единому словарю."""
    if isinstance(product, dict):
        values = [product[key] if key in product else product.get(attr)
                  for key, attr in zip(FIELDS, ATTRIBUTES)]
    elif isinstance(product, (tuple, list)):
        if len(product) != len(FIELDS):
            raise ValueError("У варианта 27 должно быть ровно 7 полей товара")
        values = product
    else:
        values = [getattr(product, attr) for attr in ATTRIBUTES]
    data = dict(zip(ATTRIBUTES, values))
    data["name"] = _text(data["name"], "[Без названия]")
    data["genre"] = _text(data["genre"], "[Без жанра]")
    data["developer"] = _text(data["developer"], "[Без разработчика]")
    data["cover"] = _text(data["cover"], "")
    try:
        data["price"] = Decimal(str(data["price"] if data["price"] is not None else 0))
        quantity = Decimal(str(data["quantity"] if data["quantity"] is not None else 0))
        if not data["price"].is_finite() or not quantity.is_finite():
            raise ValueError("Цена и количество должны быть конечными числами")
        if quantity != quantity.to_integral_value():
            raise ValueError("Количество должно быть целым числом")
        data["quantity"] = int(quantity)
    except (InvalidOperation, TypeError) as error:
        raise ValueError("Некорректная цена или количество") from error
    return data


def indicator(quantity):
    return "много" if quantity > 5 else "мало"


def is_low_stock(quantity):
    return quantity <= 3


def format_price(price):
    """Разделители тысяч; для целой цены не показываем копейки."""
    value = Decimal(str(price))
    if not value.is_finite():
        raise ValueError("Цена должна быть конечным числом")
    if value == value.to_integral_value():
        return f"{value:,.0f}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


def product_image_path(cover):
    """Имена gta.png и пути resources/gta.png понимаются одинаково."""
    if not cover:
        return None
    path = Path(cover)
    if path.is_absolute():
        return path
    if len(path.parts) == 1:
        return BASE_DIR / "resources" / path
    return BASE_DIR / path
