# Vortex Fit:

Django + админка Unfold. Каталог (товары, фото, вкусы/фасовки, остатки) ведётся в админке.
Заявки с формы консультации приходят менеджеру в Telegram. Кнопка «Заказать в Telegram»
открывает чат с менеджером и подставляет товар, вариант и цену.

Данные покупателей (имя, телефон из формы) в базу **не сохраняются**: они только пересылаются в Telegram.

## Быстрый старт локально

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DJANGO_DEBUG=1                                   # Windows: set DJANGO_DEBUG=1
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo                              # демо-товары без фото (необязательно)
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/  Админка: http://127.0.0.1:8000/admin/
В режиме отладки без токена бота заявки печатаются в консоль.

## Telegram

1. В @BotFather: `/newbot`, получи токен, запиши в `TELEGRAM_BOT_TOKEN`.
2. Создай чат (или группу) для заявок, добавь туда бота и напиши любое сообщение.
3. Открой `https://api.telegram.org/bot<ТОКЕН>/getUpdates` и найди `"chat":{"id": ...}`. Это `TELEGRAM_CHAT_ID`
   (у групп он отрицательный).
4. `TELEGRAM_MANAGER`: юзернейм менеджера без @, на него ведёт кнопка заказа.

## Запуск на сервере (VPS с Docker)

```bash
git clone <репозиторий> vortexfit && cd vortexfit    # или загрузи папку через scp
cp .env.example .env && nano .env                      # заполни значения
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo     # по желанию
```

- DNS: A-запись домена должна указывать на IP сервера, тогда Caddy сам выпустит HTTPS.
- Файлы миграций (`shop/migrations/0001_initial.py`) создаются при первом запуске. Закоммить их в git.
- Резервная копия: `docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql`
  плюс папка с фото (том `media`).
- Обновление: `git pull && docker compose up -d --build`.

## Админка

- **Товары**: цену, бейдж, «показывать на сайте» и порядок можно править прямо в списке.
  Фото и варианты (вкус, фасовка, остаток) добавляются внутри карточки товара.
- **Остатки**: отдельная таблица, где остатки по всем вариантам правятся в один клик.
- Заказы идут через чат, поэтому остаток **не списывается автоматически**. Менеджер уменьшает его вручную.
  Когда остаток 0, на карточке показывается «Под заказ».
- Смени `ADMIN_URL` с `admin/` на что-то своё.

## Что ещё нужно сделать

- Картинки героя, иконки преимуществ и аватары отзывов всё ещё берутся с CDN Tilda
  (`static.tildacdn.ink`). Скачай их и положи в свою папку `static/`, иначе они пропадут вместе с проектом на Tilda.
- Подставь реальные телефон, e-mail и адрес в футере (`shop/templates/shop/index.html`).
- Добавь страницу политики обработки персональных данных и поставь на неё ссылку в форме.
