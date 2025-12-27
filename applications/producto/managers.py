# python
from datetime import date, timedelta
# django
from django.utils import timezone
from django.db import models

from django.shortcuts import render
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
    
class LoteManager(models.Manager):
    from django.db import models
    from django.utils import timezone
    from datetime import timedelta


    def productos_por_vencer(self, dias=30):
        """
        Retorna un queryset de lotes cuya fecha de vencimiento está dentro de los próximos `dias` días.
        """
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=dias)
        return self.filter(
            expiration_date__range=(hoy, limite),
            count__gt=0
        ).select_related('product').order_by('expiration_date')
