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
from django.contrib import messages
# local
from applications.producto.models import Product
from applications.utils import render_to_pdf
from applications.users.mixins import VentasPermisoMixin
#
from .models import Sale, SaleDetail, CarShop
from .forms import VentaForm, VentaVoucherForm
from .functions import procesar_venta


class AddCarView(VentasPermisoMixin, FormView):
    template_name = 'venta/index.html'
    form_class = VentaForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = CarShop.objects.all()
        context["total_cobrar"] = CarShop.objects.total_cobrar()
        # formulario para venta con voucher
        context['form_voucher'] = VentaVoucherForm
        return context
    
    def form_valid(self, form):
        barcode = form.cleaned_data['barcode']
        count = form.cleaned_data['count']

        # Intentamos cargar el producto, si no existe avisamos y volvemos
        try:
            producto = Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            messages.error(
                self.request,
                f"❌ El código de barras '{barcode}' no corresponde a ningún producto.",
                extra_tags='danger'
            )
            return HttpResponseRedirect(reverse('venta_app:venta-index'))
        
        obj, created = CarShop.objects.get_or_create(
            barcode=barcode,
            defaults={
                'product': Product.objects.get(barcode=barcode),
                'count': count
            }
        )
        #
        if not created:
            obj.count = obj.count + count
            obj.save()
        return super(AddCarView, self).form_valid(form)
    
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


class CarShopDeleteAll(VentasPermisoMixin, View):
    
    def post(self, request, *args, **kwargs):
        #
        CarShop.objects.all().delete()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )


class ProcesoVentaSimpleView(VentasPermisoMixin, View):
    def post(self, request, *args, **kwargs):
        # 1. Recojo el carrito
        productos_en_car = CarShop.objects.select_related('product').all()

        # 2. Busco todos los problemas de stock
        faltantes = []
        for item in productos_en_car:
            disponible = item.product.count
            solicitado = item.count
            if solicitado > disponible:
                faltantes.append(
                    (item.product.name, disponible, solicitado)
                )

        # 3. Si hay faltantes, aviso y vuelvo sin procesar
        if faltantes:
            for nombre, disp, sol in faltantes:
                messages.error(
                    request,
                    f"❌ Stock insuficiente para '{nombre}': disponible {disp}, solicitado {sol}.",
                    extra_tags='danger'
                )
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        # 4. Si todo OK, proceso la venta
        venta = procesar_venta(
            self=self,
            type_invoce=Sale.SIN_COMPROBANTE,
            type_payment=Sale.CASH,
            user=self.request.user,
        )
        messages.success(request, "✔️ Venta procesada correctamente.", extra_tags='success')
        return HttpResponseRedirect(reverse('venta_app:venta-index'))

class ProcesoVentaVoucherView(VentasPermisoMixin, FormView):
    form_class  = VentaVoucherForm
    success_url = '.'

    def form_valid(self, form):
        # 1. Pre-check de stock
        productos_en_car = CarShop.objects.select_related('product').all()
        faltantes = []
        for item in productos_en_car:
            if item.count > item.product.count:
                faltantes.append((item.product.name, item.product.count, item.count))

        if faltantes:
            for nombre, disp, sol in faltantes:
                messages.error(
                    self.request,
                    f"❌ Stock insuficiente para '{nombre}': disponible {disp}, solicitado {sol}.",
                    extra_tags='danger'
                )
            return HttpResponseRedirect(reverse('venta_app:venta-index'))

        # 2. Si pasa, llamo a procesar_venta
        type_payment = form.cleaned_data['type_payment']
        type_invoce  = form.cleaned_data['type_invoce']
        venta = procesar_venta(
            self=self,
            type_invoce=type_invoce,
            type_payment=type_payment,
            user=self.request.user,
        )

        if venta:
            return HttpResponseRedirect(
                reverse('venta_app:venta-voucher_pdf', kwargs={'pk': venta.pk})
            )
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

    


