# In your models.py file
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.core.exceptions import ValidationError

# ------------------------
# Categories
# ------------------------
class Categories(models.Model):
    icon = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_all_category(self):
        return Categories.objects.all().order_by('-id')

# ------------------------
# Region
# ------------------------
class Region(models.Model):
    logo = models.ImageField(upload_to="author")
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

# ------------------------
# Duration
# ------------------------
class Duration(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

# ------------------------
# Feature
# ------------------------
class Feature(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

# ------------------------
# Product
# ------------------------
class Product(models.Model):
    STATUS = (
        ('PUBLISH', 'PUBLISH'),
        ('DRAFT', 'DRAFT'),
    )

    featured_image = models.ImageField(upload_to="featuredimg", null=True)
    title = models.CharField(max_length=500)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)
    features = models.ManyToManyField(Feature, blank=True, related_name='plans')
    description = models.TextField()
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, null=True)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})

    def best_monthly_price(self):
        prices = self.prices.all()
        if not prices.exists():
            return None, None, 0

        monthly = prices.first().monthly
        max_discount = prices.aggregate(models.Max("discount"))["discount__max"] or 0

        discounted = monthly
        if max_discount:
            discounted = monthly - (monthly * (max_discount / 100))

        return monthly, discounted, max_discount

# ------------------------
# Slug Generator
# ------------------------
def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Product)

# ------------------------
# Price
# ------------------------
class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    duration = models.ForeignKey(Duration, on_delete=models.CASCADE)
    monthly = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Discount percentage (e.g., 20 for 20%)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'region', 'duration')

    def total_price(self):
        duration_val = ''.join(filter(str.isdigit, self.duration.name))
        months = int(duration_val) if duration_val else 1
        return self.monthly * months

    def discounted_price(self):
        total = self.total_price()
        if self.discount:
            return total - (total * (self.discount / 100))
        return total

    def discounted_monthly(self):
        if self.discount:
            return self.monthly - (self.monthly * (self.discount / 100))
        return self.monthly

    def __str__(self):
        return f"{self.product.title} | {self.region.name} | {self.duration.name} → ₹{self.monthly}/mo"

# ------------------------
# UTR Validation
# ------------------------
def validate_utr(value):
    if not value.isdigit() or len(value) != 12:
        raise ValidationError("UTR ID must be exactly 12 digits.")

# ------------------------
# Purchase
# ------------------------
class Purchase(models.Model):
    STATUS_CHOICES = (
        ("UNDER_REVIEW", "Under Review"),
        ("PAID", "Paid"),
        ("FAILED", "Payment Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    region = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    utr_id = models.CharField(
        max_length=12,
        unique=True,  # 👈 This is the line that was added.
        validators=[validate_utr],
        help_text="Enter a 12-digit numeric UTR ID"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="UNDER_REVIEW")
    activated_at = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def activate_package(self):
        if not self.activated_at:
            self.activated_at = date.today()
            months = int("".join(filter(str.isdigit, self.duration))) if self.duration else 1
            self.expiry_date = self.activated_at + timedelta(days=30 * months)
            self.save()

    def __str__(self):
        return f"{self.user} | {self.product.title} | ₹{self.final_price} | {self.status}"