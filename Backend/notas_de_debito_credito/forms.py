from django import forms
from .models import Nota, Concepto

class NotaDebitoForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = [
            'factura_afectada',
            'observaciones',
            # 'es_debito',  # No mostrar en el formulario
        ]
        widgets = {
            'factura_afectada': forms.Select(),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'factura_afectada': 'Factura Asociada',
            'observaciones': 'Observaciones',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.es_debito = True
        if commit:
            instance.save()
        return instance

class NotaCreditoForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = [
            'factura_afectada',
            'observaciones',
            # 'es_debito',  # No mostrar en el formulario
        ]
        widgets = {
            'factura_afectada': forms.Select(),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'factura_afectada': 'Factura Asociada',
            'observaciones': 'Observaciones',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.es_debito = False
        if commit:
            instance.save()
        return instance

class ConceptoForm(forms.ModelForm):
    class Meta:
        model = Concepto
        fields = ['descripcion', 'monto']