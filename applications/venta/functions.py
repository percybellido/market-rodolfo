from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from applications.producto.models import Product
from .models import Sale, SaleDetail, CarShop


def procesar_venta(user, **params_venta):
    """
    Procesa la venta para el usuario actual de forma atómica, segura y optimizada.
    """

    with transaction.atomic():  # Bloquea todo este proceso
        # 🔒 Bloqueamos los productos del carrito (y sus productos asociados)
        productos_en_car = (
            CarShop.objects
            .select_related('product')
            .filter(user=user)
            .select_for_update(of=('product',))
        )

        if not productos_en_car.exists():
            return None

        # ✅ Validación de stock dentro de la transacción
        for item in productos_en_car:
            if item.count > item.product.count:
                raise ValueError(
                    f"Stock insuficiente para '{item.product.name}'. "
                    f"Disponible: {item.product.count}, solicitado: {item.count}"
                )

        # 🔢 Crear venta principal
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

            # 🔁 Actualizamos stock y número de ventas (seguro dentro del bloqueo)
            producto.count = F('count') - cantidad
            producto.num_sale = F('num_sale') + cantidad
            productos_actualizados.append(producto)

            total_cantidad += cantidad
            total_monto += cantidad * precio_venta

        # ✅ Guardar totales de la venta
        venta.count = round(total_cantidad, 2)
        venta.amount = round(total_monto, 2)
        venta.save()

        # 💾 Guardar detalles y actualizar productos
        SaleDetail.objects.bulk_create(detalles)
        Product.objects.bulk_update(productos_actualizados, ['count', 'num_sale'])

        # 🧹 Eliminar carrito
        productos_en_car.delete()

        return venta
