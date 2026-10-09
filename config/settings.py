import os
from pathlib import Path

from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=""):
    return os.environ.get(name, default)


def env_list(name, default=""):
    return [x.strip() for x in env(name, default).split(",") if x.strip()]


DEBUG = env("DJANGO_DEBUG", "0") == "1"
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
if not DEBUG and SECRET_KEY.startswith("dev-only"):
    raise RuntimeError("Задай DJANGO_SECRET_KEY в .env")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
# Render сам задаёт имя хоста сервиса, добавляем его автоматически
RENDER_HOST = env("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")
ADMIN_URL = env("ADMIN_URL", "admin/")  # лучше сменить, например на "panel-x7k2/"

INSTALLED_APPS = [
    "unfold",  # должен идти ДО django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- База данных: PostgreSQL, если задан POSTGRES_DB, иначе SQLite ---
(BASE_DIR / "data").mkdir(exist_ok=True)
if env("DATABASE_URL"):
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=600, ssl_require=True)
    }
elif env("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST", "db"),
            "PORT": env("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data" / "db.sqlite3",
        }
    }

# Кэш нужен только для ограничения частоты заявок (общий для всех воркеров)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(BASE_DIR / "data" / "cache"),
    }
}

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Фото в облаке Cloudinary (нужно там, где диск временный, например на бесплатном Render)
if env("CLOUDINARY_URL"):
    INSTALLED_APPS.insert(INSTALLED_APPS.index("django.contrib.staticfiles"), "cloudinary_storage")
    INSTALLED_APPS.append("cloudinary")
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# --- Telegram ---
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
TELEGRAM_MANAGER = env("TELEGRAM_MANAGER", "leeartur23").lstrip("@")

# --- Тема админки Unfold ---
ORANGE = {
    "50": "255 247 237", "100": "255 237 213", "200": "254 215 170",
    "300": "253 186 116", "400": "251 146 60", "500": "249 115 22",
    "600": "234 88 12", "700": "194 65 12", "800": "154 52 18",
    "900": "124 45 18", "950": "67 20 7",
}

UNFOLD = {
    "SITE_TITLE": "Vortex Fit",
    "SITE_HEADER": "Vortex Fit",
    "SITE_SUBHEADER": "Управление магазином",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "8px",
    "COLORS": {"primary": ORANGE},
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Магазин",
                "separator": False,
                "items": [
                    {"title": "Товары", "icon": "inventory_2",
                     "link": reverse_lazy("admin:shop_product_changelist")},
                    {"title": "Остатки", "icon": "warehouse",
                     "link": reverse_lazy("admin:shop_productvariant_changelist")},
                    {"title": "Категории", "icon": "category",
                     "link": reverse_lazy("admin:shop_category_changelist")},
                ],
            },
            {
                "title": "Доступ",
                "separator": True,
                "items": [
                    {"title": "Пользователи", "icon": "person",
                     "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "Группы", "icon": "group",
                     "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
        ],
    },
}
