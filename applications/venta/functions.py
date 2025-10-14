#
from decimal import Decimal
from django.utils import timezone
from django.db.models import Prefetch
#
from applications.producto.models import Product
from applications.users.models import User
#
from .models import Sale, SaleDetail, CarShop


from django.db import transaction
from django.utils import timezone
from django.db.models import F, Prefetch
from applications.producto.models import Product
from applications.users.models import User
from .models import Sale, SaleDetail, CarShop


def procesar_venta(user, **params_venta):
    """
    Procesa la venta para el usuario actual de forma atómica y optimizada.
    """

    # Prefetch para evitar consultas N+1
    productos_en_car = (
        CarShop.objects
        .filter(user=user)
        .select_related('product')
    )

    if not productos_en_car.exists():
        return None

    # ✅ Validación de stock en una sola pasada
    for item in productos_en_car:
        if item.count > item.product.count:
            raise ValueError(
                f"Stock insuficiente para '{item.product.name}'. "
                f"Disponible: {item.product.count}, solicitado: {item.count}"
            )

    with transaction.atomic():  # 👈 evita inconsistencias si algo falla
        venta = Sale.objects.create(
            date_sale=timezone.now(),
            count=Decimal('0.00'),
            amount=Decimal('0.00'),
            type_invoce=params_venta.get('type_invoce'),
            type_payment=params_venta.get('type_payment'),
            user=user
        )

        detalles = []
        productos_actualizados = []

        total_cantidad = Decimal('0.00')
        total_monto = Decimal('0.00')

        for item in productos_en_car:
            producto = item.product
            cantidad = Decimal(item.count)
            precio_venta = Decimal(producto.sale_price)

            detalles.append(
                SaleDetail(
                    sale=venta,
                    product=producto,
                    count=cantidad,
                    price_purchase=producto.purchase_price,
                    price_sale=precio_venta,
                    tax=Decimal('0.18'),
                )
            )

            # Actualización del stock en memoria
            producto.count = F('count') - cantidad
            producto.num_sale = F('num_sale') + cantidad
            productos_actualizados.append(producto)

            total_cantidad += cantidad
            total_monto += cantidad * precio_venta

        # Guardamos la venta actualizada
        venta.count = round(total_cantidad, 2)
        venta.amount = round(total_monto, 2)
        venta.save()

        # Guardamos detalles y actualizamos productos
        SaleDetail.objects.bulk_create(detalles)
        Product.objects.bulk_update(productos_actualizados, ['count', 'num_sale'])

        # Eliminamos carrito del usuario
        productos_en_car.delete()

        return venta

    