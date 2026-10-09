from django.core.management.base import BaseCommand

from shop.models import Category, Product, ProductVariant

# Цены — ориентировочные, замени на свои в админке
DEMO = [
    ("Протеин", "Vortex Whey 900 г", "vortex-whey-900", 520000, None, "Хит",
     "Быстрый сывороточный протеин для роста и восстановления мышц. 27 г белка в порции, без добавленного сахара.",
     [("Шоколад", "900 г", 25), ("Ваниль", "900 г", 12), ("Клубника", "900 г", 0)]),
    ("Креатин", "Vortex Creatine 300 г", "vortex-creatine-300", 280000, None, "",
     "Микронизированный моногидрат для прироста силы и мощности. 60 порций.",
     [("", "300 г", 40)]),
    ("BCAA", "Vortex BCAA 400 г", "vortex-bcaa-400", 330000, 412000, "−20%",
     "Аминокислоты 2:1:1 для защиты мышц от распада и ускоренного восстановления.",
     [("Арбуз", "400 г", 8), ("Лимон", "400 г", 3)]),
    ("Пре-воркаут", "Vortex Energy 250 г", "vortex-energy-250", 250000, None, "Новинка",
     "Заряд концентрации и выносливости: кофеин, бета-аланин и цитруллин.",
     [("Кола", "250 г", 15), ("Тропик", "250 г", 6)]),
    ("Гейнер", "Vortex Mass 1500 г", "vortex-mass-1500", 480000, None, "",
     "Высококалорийная смесь для набора массы: протеин, сложные углеводы и креатин в одной порции.",
     [("Шоколад", "1500 г", 10)]),
    ("Витамины", "Vortex Omega-3 90 капс.", "vortex-omega3-90", 190000, None, "",
     "Омега-3 с высокой концентрацией EPA/DHA. БАД, не является лекарственным средством.",
     [("", "90 капс.", 30)]),
]


class Command(BaseCommand):
    help = "Создаёт демо-каталог (без фото). Безопасно запускать повторно."

    def handle(self, *args, **options):
        for i, (cat, name, slug, price, old, badge, descr, variants) in enumerate(DEMO):
            category, _ = Category.objects.get_or_create(name=cat, defaults={"sort_order": i})
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults=dict(category=category, name=name, price=price, old_price=old,
                              badge=badge, description=descr, sort_order=i),
            )
            if created:
                for j, (flavor, size, stock) in enumerate(variants):
                    ProductVariant.objects.create(
                        product=product, flavor=flavor, size=size, stock=stock, sort_order=j)
        self.stdout.write(self.style.SUCCESS("Демо-каталог готов. Фото добавь в админке."))
