from django import forms
from django.forms import ModelForm
from .models import OrdenDeEntrega, ProductoEntrega

class OrdenDeEntregaForm(ModelForm):
    class Meta:
        model = OrdenDeEntrega
        fields = [
            'factura_afectada',
            'direccion_entrega',
            'observaciones'
        ]
        widgets = {
            'factura_afectada': forms.Select(),
            'direccion_entrega': forms.TextInput(),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'factura_afectada': 'Factura Asociada',
            'direccion_entrega': 'Dirección de Entrega',
            'observaciones': 'Observaciones',
        }

class ProductoEntregaForm(ModelForm):
    class Meta:
        model = ProductoEntrega
        fields = ['descripcion', 'cantidad_entregada', 'monto_unitario']