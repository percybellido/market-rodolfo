# django
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View,
    DeleteView,
    ListView
)
from django.views.generic.edit import (
    FormView
)
from django.db.models import F
from django.db import transaction
from django.contrib import messages
# local
from applications.producto.models import Product
from applications.utils import render_to_pdf
from applications.users.models import User
from applications.users.mixins import VentasPermisoMixin
#
from .models import Sale, SaleDetail, CarShop
from .forms import VentaForm, VentaVoucherForm
from .functions import procesar_venta


from django.db import transaction

class AddCarView(VentasPermisoMixin, FormView):
    template_name = 'venta/index.html'
    form_class = VentaForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["productos"] = CarShop.objects.productos_en_carrito(user)
        context["total_cobrar"] = CarShop.objects.total_cobrar(user)
        context['form_voucher'] = VentaVoucherForm()
        return context

    @transaction.atomic
    def form_valid(self, form):
        user = self.request.user
        barcode = form.cleaned_data.get('barcode')
        product = form.cleaned_data.get('product')
        count = form.cleaned_data.get('count')

        # 🧩 Caso 1: con código de barras
        if barcode:
            try:
                product_obj = Product.objects.get(barcode=barcode)
            except Product.DoesNotExist:
                messages.error(
                    self.request,
                    f"❌ El código de barras '{barcode}' no corresponde a ningún producto.",
                    extra_tags='danger'
                )
                return HttpResponseRedirect(reverse('venta_app:venta-index'))

        # 🧩 Caso 2: sin código de barras
        elif product:
            productos = Product.objects.filter(
                barcode__isnull=True,
                name__icontains=product
            )
            if productos.count() == 1:
                product_obj = productos.first()
            elif productos.count() > 1:
                messages.warning(
                    self.request,
                    f"⚠️ Se encontraron {productos.count()} coincidencias para '{product}', refine la búsqueda.",
                    extra_tags='warning'
                )
                return HttpResponseRedirect(reverse('venta_app:venta-index'))
            else:
                messages.error(
                    self.request,
                    f"❌ No se encontró ningún producto llamado '{product}'.",
                    extra_tags='danger'
                )
                return HttpResponseRedirect(reverse('venta_app:venta-index'))
        else:
            messages.error(
                self.request,
                "❌ Debes ingresar un código de barras o el nombre del producto.",
                extra_tags='danger'
            )
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        # 🧾 Agregar o actualizar producto en el carrito del usuario
        barcode_value = product_obj.barcode or None

        obj, created = CarShop.objects.get_or_create(
            user=user,
            product=product_obj,
            defaults={'count': count, 'barcode': barcode_value}
        )

        if not created:
            obj.count = obj.count + count
            obj.save(update_fields=['count'])

        return super().form_valid(form)


    
class CarShopAddView(VentasPermisoMixin, View):
    """ aumenta en 1 la cantidad en un carshop """

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        updated = CarShop.objects.filter(id=pk).update(count=F('count') + 1)

        if not updated:
            messages.error(request, "Producto no encontrado en el carrito.")

        return HttpResponseRedirect(reverse('venta_app:venta-index'))

class CarShopUpdateView(VentasPermisoMixin, View):
    """ quita en 1 la cantidad en un carshop """

    def post(self, request, *args, **kwargs):
        car = CarShop.objects.get(id=self.kwargs['pk'])
        if car.count > 1:
            car.count = car.count - 1
            car.save()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )


class CarShopDeleteView(VentasPermisoMixin, DeleteView):
    model = CarShop
    success_url = reverse_lazy('venta_app:venta-index')

    def get_queryset(self):
        # Evita que un usuario borre productos del carrito de otro
        return CarShop.objects.filter(user=self.request.user)



class CarShopDeleteAll(VentasPermisoMixin, View):

    def post(self, request, *args, **kwargs):
        CarShop.objects.limpiar_carrito(request.user)
        return HttpResponseRedirect(reverse('venta_app:venta-index'))



from django.db import DatabaseError

class ProcesoVentaSimpleView(VentasPermisoMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            venta = procesar_venta(
                user=request.user,
                type_invoce=Sale.SIN_COMPROBANTE,
                type_payment=Sale.CASH,
            )
        except ValueError as e:
            messages.error(request, str(e), extra_tags='danger')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        except DatabaseError:
            messages.warning(request, "Otro usuario está procesando productos. Intenta nuevamente.", extra_tags='warning')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        except Exception as e:
            messages.error(request, f"Error inesperado: {e}", extra_tags='danger')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        if not venta:
            messages.warning(request, "No hay productos en el carrito.", extra_tags='warning')
        else:
            messages.success(request, "✔️ Venta procesada correctamente.", extra_tags='success')

        return HttpResponseRedirect(reverse('venta_app:venta-index'))
    
class ProcesoVentaVoucherView(VentasPermisoMixin, FormView):
    form_class  = VentaVoucherForm
    success_url = '.'

    @transaction.atomic
    def form_valid(self, form):
        user = self.request.user
        type_payment = form.cleaned_data['type_payment']
        type_invoce = form.cleaned_data['type_invoce']
        try:
            venta = procesar_venta(
                user=user,
                type_invoce=type_invoce,
                type_payment=type_payment
            )
        except ValueError as e:
            messages.error(self.request, str(e), extra_tags='danger')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        except DatabaseError:
            messages.warning(self.request, "Otro usuario está procesando productos. Intenta nuevamente.", extra_tags='warning')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        except Exception as e:
            messages.error(self.request, f"Error inesperado: {e}", extra_tags='danger')
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        if venta:
            return HttpResponseRedirect(reverse('venta_app:venta-voucher_pdf', kwargs={'pk': venta.pk}))

        messages.error(self.request, "No se pudo procesar la venta.", extra_tags='danger')
        return HttpResponseRedirect(reverse('venta_app:venta-index'))

class VentaVoucherPdf(VentasPermisoMixin, View):
    
    def get(self, request, *args, **kwargs):
        venta = Sale.objects.get(id=self.kwargs['pk'])
        detalles = SaleDetail.objects.filter(sale__id=self.kwargs['pk'])

        # Agregar subtotal a cada item
        for detalle in detalles:
            detalle.subtotal = detalle.count * detalle.price_sale

        data = {
            'venta': venta,
            'detalle_productos': detalles,
        }
        pdf = render_to_pdf('venta/voucher.html', data)

        # 👇 Aquí se aplica la cabecera inline
        return HttpResponse(
            pdf,
            content_type='application/pdf',
            headers={'Content-Disposition': 'inline; filename="voucher.pdf"'}
        )

    

class SaleListView(VentasPermisoMixin, ListView):
    template_name = 'venta/ventas.html'
    context_object_name = "ventas" 

    def get_queryset(self):
        return Sale.objects.ventas_no_cerradas()



class SaleDeleteView(VentasPermisoMixin, DeleteView):
    template_name = "venta/delete.html"
    model = Sale
    success_url = reverse_lazy('venta_app:venta-index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.anulate = True
        self.object.save()
        # actualizmos sl stok y ventas
        SaleDetail.objects.restablecer_stock_num_ventas(self.object.id)
        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)

    


