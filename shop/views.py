import html
import json
import re

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import Product
from .telegram import send_telegram
from .utils import stock_text, telegram_order_url

GOALS = {
    "mass": "Набор мышечной массы",
    "cut": "Снижение веса, сушка",
    "strength": "Рост силы и выносливости",
    "health": "Витамины и общее самочувствие",
}
LEADS_PER_HOUR = 5


@ensure_csrf_cookie
def index(request):
    qs = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images", "variants")
    )
    products = []
    for p in qs:
        p.imgs = list(p.images.all())
        p.vars = list(p.variants.all())
        default = next((v for v in p.vars if v.stock > 0), p.vars[0] if p.vars else None)
        p.default = default
        if default:
            p.cur_price = default.final_price
            p.cur_stock = default.stock
            label = default.label
            show_old = default.price is None
        else:  # товар без вариантов считаем доступным
            p.cur_price, p.cur_stock, label, show_old = p.price, 99, "", True
        p.cur_old = p.old_price if (show_old and p.old_price) else None
        p.stock_text = stock_text(p.cur_stock)
        p.cur_url = telegram_order_url(p.name, label, p.cur_price)
        products.append(p)
    return render(request, "shop/index.html", {
        "products": products,
        "tg_manager": settings.TELEGRAM_MANAGER,
    })


def _client_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return fwd.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


@require_POST
def lead(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Некорректный запрос"}, status=400)

    # Ловушка для ботов: настоящий человек это поле не видит и не заполняет
    if data.get("website"):
        return JsonResponse({"ok": True})

    name = str(data.get("name", "")).strip()
    goal = GOALS.get(str(data.get("goal", "")), "не указана")
    digits = re.sub(r"\D", "", str(data.get("phone", "")))
    if len(digits) == 9:
        digits = "998" + digits

    errors = {}
    if not 2 <= len(name) <= 60:
        errors["name"] = "Введите имя"
    if not (len(digits) == 12 and digits.startswith("998")):
        errors["phone"] = "Введите номер в формате +998 (XX) XXX-XX-XX"
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    key = f"lead:{_client_ip(request)}"
    count = cache.get(key, 0)
    if count >= LEADS_PER_HOUR:
        return JsonResponse(
            {"ok": False, "error": "Слишком много заявок. Попробуйте позже."}, status=429)
    cache.set(key, count + 1, 3600)

    text = (
        "🔥 <b>Новая заявка на консультацию</b>\n"
        f"Имя: {html.escape(name)}\n"
        f"Телефон: +{digits}\n"
        f"Цель: {html.escape(goal)}\n"
        f"Время: {timezone.localtime().strftime('%d.%m.%Y %H:%M')}"
    )
    if not send_telegram(text):
        return JsonResponse(
            {"ok": False, "error": "Не удалось отправить заявку. Напишите нам в Telegram или позвоните."},
            status=502)
    return JsonResponse({"ok": True})
