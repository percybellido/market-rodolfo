from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView,
    ListView
)
from applications.venta.models import Sale, SaleDetail
from applications.producto.models import Product
from applications.users.mixins import AdminPermisoMixin
#
from .forms import LiquidacionProviderForm, ResumenVentasForm
#
from .functions import detalle_resumen_ventas

from django.conf import settings

from django.urls import reverse
from .forms import ContactForm
from django.core.mail import send_mail



class HomeView(TemplateView):
    template_name="home/inicio.html"


class PanelAdminView(AdminPermisoMixin, TemplateView):
    template_name = "home/administrador.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_ventas"] = Sale.objects.total_ventas_dia()
        context["total_anulaciones"] = Sale.objects.total_ventas_anuladas_dia()
        context["por_vencer"] = Product.objects.productos_por_vencer().count()
        context["resumen_semana"] = SaleDetail.objects.resumen_ventas()[:7]
        return context
    

class ReporteAdmin(AdminPermisoMixin, ListView):
    template_name = "home/reporte_admin.html"
    context_object_name = "resumen_ventas_mes"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_ventas"] = Sale.objects.total_ventas()
        return context
    
    def get_queryset(self):
        return SaleDetail.objects.resumen_ventas_mes()
    


class ReporteLiquidacion(AdminPermisoMixin, ListView):
    template_name = "home/reporte_liquidacion.html"
    context_object_name = "ventas_liquidacion"
    extra_context = {'form': LiquidacionProviderForm}
    
    def get_queryset(self):
        
        lista_ventas, total_ventas = SaleDetail.objects.resumen_ventas_proveedor(
            provider=self.request.GET.get("provider", ''),
            date_start=self.request.GET.get("date_start", ''),
            date_end=self.request.GET.get("date_end", ''),
        )
        self.extra_context.update({'total_ventas': total_ventas})
        return lista_ventas


class ReporteResumenVentas(AdminPermisoMixin, ListView):
    template_name = "home/resumen_ventas.html"
    context_object_name = "resumen_ventas"
    extra_context = {'form': ResumenVentasForm}
    
    def get_queryset(self):
        
        lista_ventas = detalle_resumen_ventas(
            self.request.GET.get("date_start", ''),
            self.request.GET.get("date_end", ''),
        )
        return lista_ventas
def about(request):
    return render(request, "home/about.html")

def contact(request):
    contact_form=ContactForm()

    if request.method=="POST":
        contact_form=ContactForm(data=request.POST)
        if contact_form.is_valid():
            name=request.POST.get('name', '')
            email=request.POST.get('email', '')
            content=request.POST.get('content', '')

            email_from=settings.EMAIL_HOST_USER

            recipient_list=["pbellido0401@gmail.com"]

            send_mail(name, content, email_from, recipient_list )
            #Suponemos que todo a ido bien redireccionamos
            return redirect(reverse('contact')+"?ok=1")

    return render(request, "home/contact.html", {'form':contact_form})