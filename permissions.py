def role_of(user):
    return user[5] if user is not None and len(user) == 6 else None


def can_order(user):
    return role_of(user) in ("Клиент", "Менеджер", "Администратор")


def can_view_orders(user):
    return role_of(user) in ("Менеджер", "Администратор")


def is_admin(user):
    return role_of(user) == "Администратор"


def require_order_create(user):
    if not can_order(user):
        raise PermissionError("Для оформления заказа войдите в систему")


def require_order_view(user):
    if not can_view_orders(user):
        raise PermissionError("Список и состав заказов доступны Менеджеру и Администратору")


def require_admin(user):
    if not is_admin(user):
        raise PermissionError("Редактирование доступно только Администратору")
