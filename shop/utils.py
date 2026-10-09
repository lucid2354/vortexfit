from urllib.parse import quote

from django.conf import settings


def money(value, sep="\u00a0"):
    """520000 -> '520 000' (неразрывный пробел для вёрстки)."""
    return f"{int(value):,}".replace(",", sep)


def stock_text(stock):
    if stock <= 0:
        return "Под заказ"
    if stock <= 5:
        return f"Осталось {stock}"
    return "В наличии"


def order_message(name, label, price):
    label_part = f" ({label})" if label else ""
    return f"Здравствуйте! Хочу заказать: {name}{label_part} — {money(price, ' ')} сум"


def telegram_order_url(name, label, price):
    text = order_message(name, label, price)
    return f"https://t.me/{settings.TELEGRAM_MANAGER}?text={quote(text, safe='')}"
