from model_utils.models import TimeStampedModel
from django.utils import timezone
from django.db import models
from decimal import Decimal
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from .managers import ProductManager, LoteManager

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
    # thumbnail_small: para listados (ej. 200x200, recorta si hace falta)
    thumbnail_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 75}
    )

    # thumbnail_medium: para detalle (ej. 400x300 manteniendo proporción)
    thumbnail_medium = ImageSpecField(
        source='image',
        processors=[ResizeToFit(400, 300)],
        format='JPEG',
        options={'quality': 85}
    )
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
    
    @property
    def fecha_vencimiento_proxima(self):
        """Devuelve la fecha del lote más próximo a vencer o None si no hay lotes"""
        lote = self.lotes.filter(expiration_date__gte=timezone.now().date()).order_by('expiration_date').first()
        return lote.expiration_date if lote else None
    
    class Meta:
        verbose_name='Producto'
        verbose_name_plural='Productos'

    def __str__(self):
        return str(self.id)+'-'+self.name
    
class Lote(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lotes')
    expiration_date = models.DateField('Fecha de vencimiento', blank=True, null=True)
    count = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cantidad disponible en este lote (permite decimales, ej. 1.5 kg)"
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de compra del lote"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects=LoteManager()

    class Meta:
        ordering = ['expiration_date']

    def __str__(self):
        return f"Lote {self.id} - {self.product.name} (vencimiento: {self.expiration_date})"
