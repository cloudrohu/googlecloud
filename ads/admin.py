from django.contrib import admin
from .models import AdCampaign
from decimal import Decimal
from datetime import date


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "domain_name",
        "daily_budget",
        "duration",
        "total_budget_display",
        "gst_amount_display",
        "total_with_gst_display",
        "utr_id",
        "status",
        "activated_at",
        "expiry_date",
        "days_left_display",
    )

    list_filter = (
        "status",
        "duration",
        "created_at",
        "activated_at",
    )

    search_fields = (
        "domain_name",
        "user__username",
        "utr_id",
    )

    list_editable = ("status",)
    readonly_fields = (
        "total_budget_display",
        "gst_amount_display",
        "total_with_gst_display",
        "created_at",
        "activated_at",
        "expiry_date",
    )

    ordering = ("-id",)
    list_per_page = 25

    # -----------------------------
    # Custom display methods
    # -----------------------------
    def total_budget_display(self, obj):
        return f"₹{obj.total_budget}"
    total_budget_display.short_description = "Ad Budget (No GST)"

    def gst_amount_display(self, obj):
        return f"₹{obj.gst_amount}"
    gst_amount_display.short_description = "GST (18%)"

    def total_with_gst_display(self, obj):
        return f"₹{obj.total_with_gst}"
    total_with_gst_display.short_description = "Total (Incl. GST)"

    def days_left_display(self, obj):
        return f"{obj.days_left} days" if obj.days_left is not None else "-"
    days_left_display.short_description = "Days Left"

    # -----------------------------
    # Admin Actions
    # -----------------------------
    actions = ["activate_selected_campaigns", "expire_selected_campaigns"]

    @admin.action(description="✅ Activate selected campaigns")
    def activate_selected_campaigns(self, request, queryset):
        count = 0
        for campaign in queryset:
            if campaign.status != "PAID":
                campaign.activate_campaign()
                count += 1
        self.message_user(request, f"{count} campaign(s) activated successfully.")

    @admin.action(description="⏰ Mark selected campaigns as expired")
    def expire_selected_campaigns(self, request, queryset):
        count = 0
        for campaign in queryset:
            if campaign.status == "PAID" and campaign.expiry_date and date.today() > campaign.expiry_date:
                campaign.status = "EXPIRED"
                campaign.save()
                count += 1
        self.message_user(request, f"{count} campaign(s) marked as expired.")
