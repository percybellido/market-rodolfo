from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver

# local apps
from applications.producto.models import Product
from .models import SaleDetail


@receiver(post_save, sender=SaleDetail)
def update_stock_ventas_producto(sender, instance, created, **kwargs):
    """
    ✅ Actualiza el stock y el número de ventas del producto 
    cada vez que se crea un SaleDetail (detalle de venta).
    """
    if created:  # solo cuando se crea, no en cada actualización
        producto = instance.product

        # Usamos F() para evitar condiciones de carrera
        producto.count = F('count') - instance.count
        producto.num_sale = F('num_sale') + instance.count

        producto.save(update_fields=['count', 'num_sale'])

