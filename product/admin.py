from django.utils.html import format_html, format_html_join
from django.contrib import admin
from .models import *


class PriceInline(admin.TabularInline):
    model = Price
    extra = 6   # kitne extra empty rows dikhaye
    fields = ('region', 'duration', 'monthly', 'discount')
    show_change_link = True



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'show_prices')
    search_fields = ('title', 'description')
    list_filter = ('status', 'category', 'created_at')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PriceInline]

    def show_prices(self, obj):
        prices = obj.prices.all()
        if not prices:
            return "-"
        return format_html(
            "<ul style='margin:0; padding-left:15px;'>"
            "{}"
            "</ul>",
            format_html_join(
                '',
                "<li>{} | {} | Monthly: ₹{} | Total: <b>₹{}</b> | Discount: {}% | Final: <span style='color:green;'><b>₹{}</b></span></li>",
                (
                    (
                        p.region.name,
                        p.duration.name,
                        p.monthly,
                        p.total_price(),
                        p.discount or 0,
                        p.discounted_price()
                    )
                    for p in prices
                )
            )
        )
    show_prices.short_description = "Prices"




@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo')


@admin.register(Duration)
class DurationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'region', 'duration', 'monthly', 'discount')
    list_filter = ('region', 'duration')
    search_fields = ('product__title',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "region",
        "duration",
        "show_final_price",
        "utr_id",
        "created_at",
    )
    search_fields = ("product__title", "user__username", "utr_id")
    list_filter = ("region", "duration", "created_at")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Purchase Info", {
            "fields": ("user", "product", "region", "duration", "final_price", "utr_id")
        }),
        ("Meta", {
            "fields": ("created_at",),
        }),
    )

    def show_final_price(self, obj):
        return format_html(
            "<span style='color:green; font-weight:bold;'>₹{}</span>",
            obj.final_price
        )
    show_final_price.short_description = "Final Price"




