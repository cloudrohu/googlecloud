from django.utils.html import format_html, format_html_join
from django.contrib import admin
from .models import *


class PriceInline(admin.TabularInline):
    model = Price
    extra = 6   # kitne extra empty rows dikhaye
    fields = ('region', 'duration', 'monthly', 'discount')
    show_change_link = True





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
            "<br>".join(
                f"<b>{p.region.name} — {p.duration.name}</b>: ₹{p.monthly}/mo → "
                f"<span style='color:green;'>₹{p.discounted_price()}</span> (SAVE {p.discount or 0}%)"
                for p in prices
            )
        )
    show_prices.short_description = "Prices"

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "region", "duration", "final_price", "status", "activated_at", "expiry_date")
    list_filter = ("status", "region", "duration")
    search_fields = ("user__username", "product__title", "utr_id")
    readonly_fields = ("created_at", "activated_at", "expiry_date")

    def save_model(self, request, obj, form, change):
        # ✅ Jab admin "Paid" kare → auto activate
        if obj.status == "PAID" and not obj.activated_at:
            obj.activate_package()
        super().save_model(request, obj, form, change)
