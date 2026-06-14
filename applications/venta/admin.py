from django.contrib import admin
from .models import Sale, SaleDetail, CarShop

admin.site.register(CarShop)


class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 0
    readonly_fields = (
        'product',
        'count',
        'price_purchase',
        'price_sale',
    )

    can_delete = False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'date_sale',
        'user',
        'amount',
        'anulate',
    )

    list_filter = (
        'anulate',
        'date_sale',
        'user',
    )

    search_fields = (
        '=id',
    )

    readonly_fields = (
        'date_sale',
        'user',
        'amount',
    )

    inlines = [SaleDetailInline]

@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        'sale',
        'product',
        'count',
    )

    readonly_fields = (
        'sale',
        'product',
        'count',
        'price_purchase',
        'price_sale',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False