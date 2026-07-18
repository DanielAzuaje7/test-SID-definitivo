from django import forms
from django.forms import inlineformset_factory
from .models import Factura, ProductoFactura

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'nombre_cliente',
            'lugar_emision',
            'telefono_cliente',
            'cedula_cliente',
            'numero_factura',
        ]
        widgets = {
            
            'numero_factura': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Se generará automáticamente'
            }),
        }

class ProductoFacturaForm(forms.ModelForm):
    class Meta:
        model = ProductoFactura
        fields = ['nombre', 'cantidad', 'precio_unitario']

ProductoFacturaFormSet = inlineformset_factory(
    Factura,
    ProductoFactura,
    form=ProductoFacturaForm,
    extra=1,
    can_delete=True
)

class FacturaEditarForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'nombre_cliente',
            'cedula_cliente',
            'telefono_cliente',
            'lugar_emision',
            
        ]
