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
            'due_date',
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
            'due_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs = {
                    'type': 'date',
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
                    'placeholder': 'Codigo de barras',
                    'class': 'form-control',
                }
            ),
            'purchase_price': forms.NumberInput(
                attrs = {
                    'placeholder': '1',
                    'class': 'form-control',
                }
            ),
            'sale_price': forms.NumberInput(
                attrs = {
                    'placeholder': '1',
                    'class': 'form-control',
                }
            ),
        }
    # validations
    def clean_barcode(self):
        barcode = self.cleaned_data['barcode']
        if len(barcode) < 11:
            raise forms.ValidationError('Ingrese un codigo de barras correcto')

        return barcode
    
    def clean_purchase_price(self):
        purchase_price = self.cleaned_data['purchase_price']
        if not purchase_price > 0:
            raise forms.ValidationError('Ingrese un precio compra mayor a cero')

        return purchase_price
    
    def clean_sale_price(self):
        sale_price = self.cleaned_data['sale_price']
        purchase_price = self.cleaned_data.get('purchase_price')
        if not sale_price >= purchase_price:
            raise forms.ValidationError('El precio de venta debe ser mayor o igual que el precio de compra')

        return sale_price
