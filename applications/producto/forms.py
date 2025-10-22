# django
from django import forms
# local
from .models import Product


class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = (
            'barcode',
            'name',
            'provider',
            'marca',
            'description',
            'unit',
            'count',
            'purchase_price',
            'sale_price',
        )
        widgets = {
            'barcode': forms.TextInput(
                attrs = {
                    'placeholder': 'Codigo de barras',
                    'class': 'form-control',
                    'autofocus': 'autofocus',
                }
            ),
            'name': forms.TextInput(
                attrs = {
                    'placeholder': 'Nombre...',
                    'class': 'form-control',
                }
            ),
            'description': forms.Textarea(
                attrs = {
                    'placeholder': 'Descripcion del producto',
                    'rows': '3',
                    'class': 'form-control',
                }
            ),
            'unit': forms.Select(
                attrs = {
                    'class': 'form-control',
                }
            ),
            'count': forms.NumberInput(
                attrs = {
                    'placeholder': 'Cantidad',
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),
            'purchase_price': forms.NumberInput(
                attrs = {
                    'placeholder': '1',
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),
            'sale_price': forms.NumberInput(
                attrs = {
                    'placeholder': '1',
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),
        }
   # Permite dejar el código de barras vacío
    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')

        # Si el usuario no ingresó nada o lo dejó vacío
        if not barcode or barcode.strip() == '':
            return None  # ✅ Se guardará como NULL en la base de datos

        # Si lo ingresó, validamos su longitud mínima
        if len(barcode) < 11:
            raise forms.ValidationError('Ingrese un código de barras válido (mínimo 11 dígitos).')

        return barcode

    def clean_purchase_price(self):
        purchase_price = self.cleaned_data.get('purchase_price')
        if purchase_price is None or purchase_price <= 0:
            raise forms.ValidationError('Ingrese un precio de compra mayor a cero.')
        return round(purchase_price, 2)

    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        purchase_price = self.cleaned_data.get('purchase_price')

        # Validamos solo si ambos valores están definidos
        if sale_price is None:
            raise forms.ValidationError('Ingrese un precio de venta.')
        if purchase_price and sale_price < purchase_price:
            raise forms.ValidationError('El precio de venta debe ser mayor o igual que el precio de compra.')

        return round(sale_price, 2)