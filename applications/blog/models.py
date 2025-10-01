from django.db import models
from django.conf import settings

from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=100, verbose_name="Nombre")
    created=models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated=models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")

    class Meta:
        verbose_name="categoría"
        verbose_name_plural="categorías"
        ordering=['-created']

    def __str__(self):
        return self.name

class Post(models.Model):
    title= models.CharField(max_length=100, verbose_name="Titulo")
    content=RichTextField(verbose_name="Contenido")
    image=models.ImageField(verbose_name="Imagen", upload_to="image_blog", null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categories=models.ManyToManyField(Category, verbose_name="Categorias", related_name="get_posts")
    created=models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")
    updated=models.DateTimeField(auto_now=True, verbose_name="Fecha de edicion")
    is_published=models.BooleanField(verbose_name="Publicado", default=False)

    class Meta:
        verbose_name="entrada"
        verbose_name_plural="entradas"
        ordering=["-created"]
    
    def __str__(self):
        return self.title