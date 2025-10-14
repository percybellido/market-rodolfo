from model_utils.models import TimeStampedModel

from django.db import models
from decimal import Decimal
from django.utils.text import slugify

from .managers import ProductManager

# Create your models here.
class Marca(TimeStampedModel):
    name=models.CharField('Nombre', max_length=30)

    class Meta:
        verbose_name='Marca'
        verbose_name_plural='Marcas'

    def __str__(self):
        return self.name
    
class Provider(TimeStampedModel):
    name=models.CharField('Razon Social', max_length=100)
    email=models.EmailField(blank=True, null=True)
    phone=models.CharField('telefono', max_length=40, blank=True)
    web=models.URLField('sitio web', blank=True)

    class Meta:
        verbose_name='Proveedor'
        verbose_name_plural='Proveedores'

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Product(TimeStampedModel):

    UNIT_CHOICES = (
        ('0', 'Kilogramos'),
        ('1', 'Litros'),
        ('2', 'Unidades'),
    )

    category=models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    barcode=models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name="Código de barras")
    name=models.CharField('Nombre', max_length=40)
    slug=models.SlugField(max_length=50, unique=True, blank=True)
    provider=models.ForeignKey(Provider, on_delete=models.CASCADE)
    marca=models.ForeignKey(Marca, on_delete=models.CASCADE)
    due_date=models.DateField('fecha de vencimiento', blank=True, null=True)
    description=models.TextField('Descripcion del Producto', blank=True)
    unit=models.CharField('unidad de medida', max_length=1, choices=UNIT_CHOICES)
    count = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cantidad disponible en stock (permite decimales, ej. 1.5 kg)"
    )

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de compra unitario"
    )
    sale_price=models.DecimalField('Precio de Venta', max_digits=7, decimal_places=2)
    num_sale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cantidad total vendida (permite decimales)"
    )
    anulate=models.BooleanField('Eliminado', default=False)
    image=models.ImageField(upload_to='uploads/product/', null=True, blank=True)
    # Add Sale Stuff
    is_sale=models.BooleanField(default=False)

    objects=ProductManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            #Genera un slug base a partir del nombre
            base_slug=slugify(self.name)
            slug=base_slug
            counter=1
            #Verifica si el slug ya existe y de ser asi lo mofica agregando un sufijo numerico
            while Product.objects.filter(slug=slug).exists():
                slug=f'{base_slug}-{counter}'
                counter+=1
            self.slug=slug
        super(Product, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name='Producto'
        verbose_name_plural='Productos'

    def __str__(self):
        return str(self.id)+'-'+self.name