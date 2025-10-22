from django.contrib import admin
from .models import Marca, Provider, Category, Product, Lote

# Register your models here.
admin.site.register(Marca)
admin.site.register(Provider)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Lote)