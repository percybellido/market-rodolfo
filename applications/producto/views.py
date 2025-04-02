from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
)

from .forms import ProductForm

class ProductListView(ListView):
    template_name="producto/lista.html"
    context_object_name='productos'
    paginate_by=8

    def get_queryset(self):
        kword=self.request.GET.get("kword", '')
        order=self.request.GET.get("order", '')
        queryset=Product.objects.buscar_producto(kword, order)
        return queryset

class ProductCreateView(CreateView):
    template_name="producto/form_producto.html"
    form_class=ProductForm
    success_url=reverse_lazy('producto_app:producto-lista')


class ProductUpdateView(UpdateView):
    template_name="producto/form_producto.html"
    model=Product
    form_class=ProductForm
    success_url=reverse_lazy('producto_app:producto-lista')

class ProductDeleteView(DeleteView):
    template_name = "producto/delete.html"
    model = Product
    success_url = reverse_lazy('producto_app:producto-lista')

class ProductDetailView(DetailView):
    template_name = "producto/detail.html"
    model = Product

    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #
        #context["ventas_mes"] = SaleDetail.objects.ventas_mes_producto(
          #  self.kwargs['pk']
        #)
        #return context


class FiltrosProductListView(ListView):
    template_name="producto/filtros.html"
    context_object_name='productos'

    def get_queryset(self):

        queryset=Product.objects.filtrar(
            kword=self.request.GET.get("kword", ''),
            date_start=self.request.GET.get("date_start", ''),
            date_end=self.request.GET.get("date_end", ''),
            provider=self.request.GET.get("provider", ''),
            marca=self.request.GET.get("marca", ''),
            order=self.request.GET.get("order", ''),
        )
        return queryset()
    
class CategoryProductListView(ListView):
    model=Product
    template_name="producto/category_list.html"
    context_object_name="productos"

    def get_queryset(self):
        category_slug=self.kwargs.get('slug')
        category=get_object_or_404(Category, slug=category_slug)
        return Product.objects.filter(category=category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar todas las categorías para el menú
        context['categories'] = Category.objects.all()
        return context
