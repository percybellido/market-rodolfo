from django.contrib import admin
from .models import Marca, Provider, Category, Product

# Register your models here.
admin.site.register(Marca)
admin.site.register(Provider)
admin.site.register(Category)
admin.site.register(Product)