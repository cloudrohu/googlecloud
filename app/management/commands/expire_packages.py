from django.core.management.base import BaseCommand
from datetime import date
from product.models import Purchase

class Command(BaseCommand):
    help = "Expire old packages"

    def handle(self, *args, **kwargs):
        purchases = Purchase.objects.filter(status="PAID", expiry_date__lt=date.today())
        for purchase in purchases:
            purchase.status = "EXPIRED"
            purchase.save()
        self.stdout.write(self.style.SUCCESS("Expired packages updated"))