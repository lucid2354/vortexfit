from django.db import models


class Category(models.Model):
    name = models.CharField("Название", max_length=60)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, verbose_name="Категория", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="products",
    )
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Слаг (для ссылки)", max_length=140, unique=True)
    description = models.TextField("Описание", blank=True)
    price = models.PositiveIntegerField("Цена, сум")
    old_price = models.PositiveIntegerField(
        "Старая цена, сум", null=True, blank=True,
        help_text="Если заполнить, на карточке появится зачёркнутая цена.",
    )
    badge = models.CharField(
        "Бейдж", max_length=20, blank=True,
        help_text="Например: Хит, Новинка, −20%.",
    )
    is_active = models.BooleanField("Показывать на сайте", default=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    created = models.DateTimeField("Создан", auto_now_add=True)
    updated = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        ordering = ["sort_order", "-id"]
        verbose_name = "товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        # .all() использует prefetch_related, если он был
        return sum(v.stock for v in self.variants.all())


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE, related_name="images",
    )
    image = models.ImageField("Фото", upload_to="products/%Y/%m/")
    alt = models.CharField("Подпись (alt)", max_length=160, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "фото"
        verbose_name_plural = "Фото"

    def __str__(self):
        return f"Фото {self.pk} — {self.product}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE, related_name="variants",
    )
    flavor = models.CharField("Вкус", max_length=60, blank=True)
    size = models.CharField("Фасовка", max_length=60, blank=True, help_text="Например: 900 г, 90 капс.")
    price = models.PositiveIntegerField(
        "Своя цена, сум", null=True, blank=True,
        help_text="Оставь пустым, чтобы взять цену товара.",
    )
    stock = models.PositiveIntegerField("Остаток, шт.", default=0)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "вариант"
        verbose_name_plural = "Остатки по вариантам"

    def __str__(self):
        return f"{self.product} — {self.label}"

    @property
    def label(self):
        return ", ".join(x for x in (self.flavor, self.size) if x) or "Стандарт"

    @property
    def final_price(self):
        return self.price if self.price is not None else self.product.price
