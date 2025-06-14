# python
from datetime import timedelta
# django
from django.utils import timezone
from django.db import models

from django.db.models import Q, F

class ProductManager(models.Manager):

    def buscar_producto(self, kword, order):
        consulta = self.filter(
            Q(name__icontains=kword) | Q(category__name__icontains=kword) | Q(barcode=kword)| Q(barcode=kword)
        )
        # verificamos en que orden se solicita
        if order == 'date':
            # ordenar por fecha
            return consulta.order_by('created')
        elif order == 'name':
            # ordenar por nombre
            return consulta.order_by('name')
        elif order == 'stock':
            return consulta.order_by('count')
        else:
            return consulta.order_by('-created')
        

    
    def filtrar(self, **filters):
        if not filters['date_start']:
            filters['date_start'] = '2020-01-01'
        
        if not filters['date_end']:
            filters['date_end'] = timezone.now().date() + timedelta(1080)
        #
        consulta = self.filter(
            due_date__range=(filters['date_start'], filters['date_end'])
        ).filter(
            Q(name__icontains=filters['kword']) | Q(barcode=filters['kword'])
        ).filter(
            marca__name__icontains=filters['marca'],
            provider__name__icontains=filters['provider'],
        )

        if filters['order'] == 'name':
            return consulta.order_by('name')
        elif filters['order'] == 'stock':
            return consulta.order_by('count')
        elif filters['order'] == 'num':
            return consulta.order_by('-num_sale')
        else:
            return consulta.order_by('-created')
        
    def productos_en_cero(self):
            #
            consulta = self.filter(
            count__lt=6
            )
            #
            return consulta