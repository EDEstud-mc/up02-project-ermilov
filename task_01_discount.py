price = float(input("Введите цену: "))
percent = float(input("Введите скидку (%): "))

discounted_price = price * (1 - percent / 100)


print(f"Цена со скидкой: {discounted_price:.2f} руб.")
