from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from django.core.exceptions import ValidationError


# -----------------------------
# ✅ UTR Validator
# -----------------------------
def validate_utr(value):
    """Ensure UTR is exactly 12 digits"""
    if not value.isdigit() or len(value) != 12:
        raise ValidationError("UTR ID must be exactly 12 digits.")


class AdCampaign(models.Model):
    # -----------------------------
    # Duration Choices
    # -----------------------------
    DURATION_CHOICES = [
        (7, "7 Days"),
        (15, "15 Days"),
        (30, "1 Month (30.4 Days)"),
    ]

    STATUS_CHOICES = [
        ("UNDER_REVIEW", "Under Review"),
        ("PAID", "Paid"),
        ("FAILED", "Payment Failed"),
        ("EXPIRED", "Expired"),
    ]

    # -----------------------------
    # Core Fields
    # -----------------------------
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=255)
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(choices=DURATION_CHOICES, default=30)
    utr_id = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_utr],
        help_text="Enter 12-digit UTR ID after payment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="UNDER_REVIEW")

    # -----------------------------
    # Decimal Safe Calculations
    # -----------------------------
    @property
    def total_budget(self):
        """Ad cost before GST"""
        if not self.daily_budget or not self.duration:
            return Decimal("0.00")

        duration_map = {
            7: Decimal("7"),
            15: Decimal("15"),
            30: Decimal("30.4"),
        }
        multiplier = duration_map.get(self.duration, Decimal("7"))
        total = Decimal(self.daily_budget) * multiplier
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def gst_amount(self):
        """18% GST"""
        gst = (self.total_budget * Decimal("0.18"))
        return gst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total_with_gst(self):
        """Total (Budget + GST)"""
        total = self.total_budget + self.gst_amount
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # -----------------------------
    # Business Logic
    # -----------------------------
    def activate_campaign(self):
        """Activate ad after payment, set expiry"""
        if not self.activated_at:
            self.activated_at = date.today()
            days = 30 if self.duration == 30 else self.duration
            self.expiry_date = self.activated_at + timedelta(days=days)
            self.status = "PAID"
            self.save()

    def check_and_update_status(self):
        """Auto-expire ads after duration"""
        if self.status == "PAID" and self.expiry_date:
            if date.today() > self.expiry_date:
                self.status = "EXPIRED"
                self.save()

    @property
    def current_status(self):
        """Always return latest valid status"""
        self.check_and_update_status()
        return self.status

    @property
    def days_left(self):
        """Days left before expiry"""
        if self.expiry_date:
            remaining = (self.expiry_date - date.today()).days
            return max(0, remaining)
        return None

    # -----------------------------
    # Validations
    # -----------------------------
    def clean(self):
        """Custom budget validations"""
        if self.daily_budget < Decimal("350"):
            raise ValidationError("Minimum daily budget must be ₹350.")
        if self.duration == 15 and self.daily_budget < Decimal("2500"):
            raise ValidationError("For 15 Days plan, daily budget must be above ₹2500.")
        if self.duration == 7 and self.daily_budget < Decimal("10000"):
            raise ValidationError("For 7 Days plan, daily budget must be above ₹10000.")

    # -----------------------------
    # Display
    # -----------------------------
    def __str__(self):
        return f"{self.user.username} → {self.domain_name} | ₹{self.daily_budget}/day | {self.status}"

    # -----------------------------
    # Meta
    # -----------------------------
    class Meta:
        verbose_name = "Ad Campaign"
        verbose_name_plural = "Ad Campaigns"
        ordering = ("-id",)
