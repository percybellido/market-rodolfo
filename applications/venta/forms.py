from django import forms
from decimal import Decimal
#local
from .models import Sale
from applications.producto.models import Product


class VentaForm(forms.Form):
    barcode = forms.CharField(
        required=False,  # 👈 antes era obligatorio
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Código de barras (opcional)',
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        )
    )
    product = forms.CharField(  # 👈 ahora es texto libre
    required=False,
    widget=forms.TextInput(
        attrs={
            'placeholder': 'Nombre del producto (si no tiene código)',
            'class': 'form-control',
        }
    )
    )
    # ✅ ahora permite decimales
    count = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'value': '1.00',
                'class': 'form-control',
                'step': '0.01',  # permite valores como 0.25, 1.50, etc.
                'min': '0.01',
            }
        )
    )

    def clean_count(self):
        """
        Validación: la cantidad debe ser positiva
        y se redondea a 2 decimales.
        """
        count = self.cleaned_data['count']
        if count <= 0:
            raise forms.ValidationError('Ingrese una cantidad mayor a cero')
        return round(count, 2)

    def clean(self):
        cleaned_data = super().clean()
        barcode = cleaned_data.get('barcode')
        product = cleaned_data.get('product')

        # 🔎 validación: debe haber al menos uno
        if not barcode and not product:
            raise forms.ValidationError(
                "Debe ingresar un código de barras o seleccionar un producto."
            )
        return cleaned_data

    

class VentaVoucherForm(forms.Form):

    type_payment = forms.ChoiceField(
        required=False,
        choices=Sale.TIPO_PAYMENT_CHOICES,
        initial=Sale.CASH,  
        widget=forms.Select(
            attrs = {
                'class': 'form-select',
            }
        )
    )
    type_invoce = forms.ChoiceField(
        required=False,
        choices=Sale.TIPO_INVOCE_CHOICES,
        widget=forms.Select(
            attrs = {
                'class': 'form-select',
            }
        )
    )