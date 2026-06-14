from django.contrib import admin
from .models import Marca, Provider, Category, Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass

admin.site.register(Marca)
admin.site.register(Provider)
admin.site.register(Category)


