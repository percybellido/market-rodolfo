from applications.producto.models import Category

def menu_categories(request):
    return {
        'categories': Category.objects.all()
    }