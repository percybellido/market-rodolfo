from django.contrib import admin
from .models import Marca, Provider, Category, Product, Lote

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('count',)

admin.site.register(Marca)
admin.site.register(Provider)
admin.site.register(Category)

admin.site.register(Lote)