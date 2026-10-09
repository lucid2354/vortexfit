import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Первичная настройка без доступа к консоли (бесплатный Render): "
        "создаёт админа из DJANGO_SUPERUSER_* и, если SEED_DEMO=1, демо-товары."
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        if username and password:
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                self.stdout.write("Админ уже существует, пропускаю.")
            else:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f"Создан админ «{username}»."))
        else:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD не заданы, админ не создан.")

        if os.environ.get("SEED_DEMO") == "1":
            call_command("seed_demo")
