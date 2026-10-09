import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)


def send_telegram(text):
    """Отправляет HTML-сообщение в чат менеджера. Возвращает True/False."""
    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        if settings.DEBUG:
            print("\n[TELEGRAM, режим отладки]\n" + text + "\n")
            return True
        log.error("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID не заданы")
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML",
                  "disable_web_page_preview": True},
            timeout=8,
        )
        if r.status_code != 200:
            log.error("Telegram вернул %s: %s", r.status_code, r.text[:200])
            return False
        return True
    except requests.RequestException as exc:
        log.error("Ошибка отправки в Telegram: %s", exc)
        return False
