from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Product, ProductImage, ProductVariant
from .utils import money


def _stock_badge(stock):
    if stock <= 0:
        color, text = "#dc2626", "нет в наличии"
    elif stock <= 5:
        color, text = "#d97706", f"{stock} шт. (мало)"
    else:
        color, text = "#16a34a", f"{stock} шт."
    return format_html('<b style="color:{}">{}</b>', color, text)


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "preview", "alt", "sort_order")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:56px;width:56px;object-fit:cover;border-radius:8px">',
                obj.image.url,
            )
        return "—"


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("flavor", "size", "price", "stock", "sort_order")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("thumb", "name", "category", "price", "badge",
                    "stock_col", "is_active", "sort_order")
    list_display_links = ("thumb", "name")
    # Эти поля можно менять прямо в списке, не открывая карточку
    list_editable = ("price", "badge", "is_active", "sort_order")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]
    actions = ["hide", "show", "mark_hit", "clear_badge"]
    list_per_page = 50
    fieldsets = (
        ("Основное", {"fields": ("name", "slug", "category", "description")}),
        ("Цена и показ", {"fields": ("price", "old_price", "badge", "is_active", "sort_order")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category").prefetch_related("images", "variants")

    @admin.display(description="Фото")
    def thumb(self, obj):
        img = next(iter(obj.images.all()), None)
        if img and img.image:
            return format_html(
                '<img src="{}" style="height:44px;width:44px;object-fit:cover;border-radius:8px">',
                img.image.url,
            )
        return "—"

    @admin.display(description="Остаток")
    def stock_col(self, obj):
        if not obj.variants.all():
            return "—"
        return _stock_badge(obj.total_stock)

    @admin.action(description="Скрыть выбранные товары с сайта")
    def hide(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, f"Скрыто товаров: {n}")

    @admin.action(description="Показать выбранные товары на сайте")
    def show(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f"Показано товаров: {n}")

    @admin.action(description="Поставить бейдж «Хит»")
    def mark_hit(self, request, queryset):
        n = queryset.update(badge="Хит")
        self.message_user(request, f"Бейдж «Хит» поставлен: {n}")

    @admin.action(description="Убрать бейдж")
    def clear_badge(self, request, queryset):
        n = queryset.update(badge="")
        self.message_user(request, f"Бейдж убран: {n}")


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    """Быстрая страница остатков: правим цифры прямо в таблице."""
    list_display = ("product", "variant_label", "price_col", "stock", "stock_state")
    list_editable = ("stock",)
    list_filter = ("product__category", "product")
    search_fields = ("product__name", "flavor", "size")
    list_per_page = 100

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")

    @admin.display(description="Вариант")
    def variant_label(self, obj):
        return obj.label

    @admin.display(description="Цена")
    def price_col(self, obj):
        return f"{money(obj.final_price)} сум"

    @admin.display(description="Статус")
    def stock_state(self, obj):
        return _stock_badge(obj.stock)
