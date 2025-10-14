from django.db import models
from decimal import Decimal
from django.conf import settings

from django.utils import timezone
#
from model_utils.models import TimeStampedModel

# local apps
from applications.producto.models import Product

#
from .managers import SaleManager, SaleDetailManager, CarShopManager


class Sale(TimeStampedModel):
    """Modelo que representa a una Venta Global"""

    # tipo recibo constantes
    BOLETA = '0'
    FACTURA = '1'
    SIN_COMPROBANTE = '2'
    # tipo pago constantes
    TARJETA = '0'
    CASH = '1'
    BONO = '2'
    OTRO = '3'
    #
    TIPO_INVOCE_CHOICES = [
        (BOLETA, 'Boleta'),
        (FACTURA, 'Factura'),
        (SIN_COMPROBANTE, 'Sin Comprobante'),
    ]

    TIPO_PAYMENT_CHOICES = [
        (TARJETA, 'Tarjeta'),
        (CASH, 'Cash'),
        (BONO, 'Bono'),
        (OTRO, 'Otro'),
    ]

    date_sale = models.DateTimeField(
        'Fecha de Venta',
    )

    date_created = models.DateTimeField(auto_now_add=True)

    count = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount = models.DecimalField(
        'Monto', 
        max_digits=10, 
        decimal_places=2
    )
    type_invoce = models.CharField(
        'TIPO',
        max_length=2,
        choices=TIPO_INVOCE_CHOICES
    )
    type_payment = models.CharField(
        'TIPO PAGO',
        max_length=2,
        choices=TIPO_PAYMENT_CHOICES
    )
    close = models.BooleanField(
        'Venta cerrada',
        default=False
    )
    anulate = models.BooleanField(
        'Venta Anulada',
        default=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='cajero',
        related_name="user_venta",
    )

    objects = SaleManager()

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'ventas'

    def __str__(self):
        return 'Nº [' + str(self.id) + '] - ' + str(self.date_sale)



class SaleDetail(TimeStampedModel):
    """Modelo que representa a una venta en detalle"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='producto',
        related_name='product_sale'
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE, 
        verbose_name='Codigo de Venta',
        related_name='detail_sale'
    )
    count = models.DecimalField(max_digits=10, decimal_places=2)
    price_purchase = models.DecimalField(
        'Precio Compra', 
        max_digits=10, 
        decimal_places=3
    )
    price_sale = models.DecimalField(
        'Precio Venta', 
        max_digits=10, 
        decimal_places=2
    )
    tax = models.DecimalField(
        'Impuesto', 
        max_digits=5,
        decimal_places=2
    )
    anulate = models.BooleanField(default=False)
    #

    objects = SaleDetailManager()

    class Meta:
        verbose_name = 'Producto Vendido'
        verbose_name_plural = 'Productos vendidos'

    def __str__(self):
        return str(self.sale.id) + ' - ' + str(self.product.name)


class CarShop(TimeStampedModel):
    """Modelo que representa a un carrito de compras asociado a un usuario del sistema"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carshops',
        verbose_name='Usuario'
    )

    barcode = models.CharField(
        max_length=13,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='producto',
        related_name='product_car'
    )
    count = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cantidad solicitada (permite decimales)"
    )
    
    objects = CarShopManager()

    class Meta:
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carrito de compras'
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.full_name} → {self.product.name} (x{self.count})"


 
