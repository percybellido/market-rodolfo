from django import forms

from applications.producto.models import Provider


class LiquidacionProviderForm(forms.Form):

    provider = forms.ModelChoiceField(
        required=True,
        queryset=Provider.objects.all(),
        widget=forms.Select(
            attrs = {
                'class': 'input-group-field',
            }
        )
    )
    date_start = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'input-group-field',
            },
        )
    )
    date_end = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'input-group-field',
            },
        )
    )


class ResumenVentasForm(forms.Form):
    
    date_start = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            },
        )
    )
    date_end = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            },
        )
    )



class ContactForm(forms.Form):
    name=forms.CharField(label="Nombre", required=True, widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Escribe tu nombre'}
    ), min_length=3, max_length=100)
    email=forms.EmailField(label="Email", required=True, widget=forms.EmailInput(
        attrs={'class':'form-control', 'placeholder':'Escribe tu email'}
    ), min_length=3, max_length=100)
    content=forms.CharField(label="Contenido", required=True, widget=forms.Textarea(
        attrs={'class':'form-control', 'placeholder':'Escribe tu mensaje'}
    ), min_length=10, max_length=1000)