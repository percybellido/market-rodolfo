from django.urls import path
from . import views

app_name="producto_app"

urlpatterns = [
    
    path('producto/lista/', views.ProductListView.as_view(), name='producto-lista'),
    path('producto/agregar/', views.ProductCreateView.as_view(), name='producto-add'),
    path('producto/agregar/<pk>/', views.ProductUpdateView.as_view(), name='producto-update'),
    path('producto/eliminar/<pk>/', views.ProductDeleteView.as_view(), name='producto-delete'),
    path('producto/detalle/<pk>', views.ProductDetailView.as_view(), name='producto-detail'),
    path('producto/reporte/', views.FiltrosProductListView.as_view(), name='producto-filtros'),
    
    path('productos/', views.CategoryProductListView.as_view(), name='product-list'),
    path('productos/categoria/<slug:slug>/', views.CategoryProductListView.as_view(), name='product-category'),
    path("productos-por-vencer/", views.productos_por_vencer_view, name="productos_por_vencer"),
]