from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver

# local apps
from applications.producto.models import Product
from .models import SaleDetail


@receiver(post_save, sender=SaleDetail)
def update_stock_ventas_producto(sender, instance, created, **kwargs):
    if created:
        producto = instance.product

        # SOLO estadísticas
        producto.num_sale = F('num_sale') + instance.count
        producto.save(update_fields=['num_sale'])

