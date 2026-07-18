from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError
from django.conf import settings
from Backend.facturas.models import Factura
from decimal import Decimal

def validar_cedula_rif(valor):
    patron = r'^(J-\d{9}|V-\d{8}|E-\d{8}|P-\d{9}|G-\d{9})$'
    if not re.match(patron, valor):
        raise ValidationError(
            'El RIF/Cédula debe tener el formato J-XXXXXXXXX, V-XXXXXXXX, E-XXXXXXXX, P-XXXXXXXXX o G-XXXXXXXXX.'
        )

# Create your models here.
class Nota(models.Model):
    factura_afectada = models.ForeignKey(Factura, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    numero_nota = models.CharField(max_length=20, unique=True)
    es_debito = models.BooleanField(default=True)  # True = Débito, False = Crédito
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    emitida = models.BooleanField(default=False)

    # Campos copiados de la factura
    lugar_emision = models.CharField(max_length=100, editable=False)
    fecha_emision = models.DateField(editable=False)
    nombre_cliente = models.CharField(max_length=100, editable=False)
    telefono_cliente = models.CharField(max_length=11, editable=False)
    cedula_cliente = models.CharField(max_length=11, editable=False)

    def save(self, *args, **kwargs):
        # Copia los datos de la factura asociada
        if self.factura_afectada:
            self.lugar_emision = self.factura_afectada.lugar_emision
            self.fecha_emision = self.factura_afectada.fecha_emision
            self.nombre_cliente = self.factura_afectada.nombre_cliente
            self.telefono_cliente = self.factura_afectada.telefono_cliente
            self.cedula_cliente = self.factura_afectada.cedula_cliente

        # Generar número de nota si no existe
        if not self.numero_nota:
            tipo = "ND" if self.es_debito else "NC"
            count = Nota.objects.filter(usuario=self.usuario, es_debito=self.es_debito).count() + 1
            while True:
                numero = f"{tipo}-{count:05d}"
                if not Nota.objects.filter(numero_nota=numero).exists():
                    self.numero_nota = numero
                    break
                count += 1

        super().save(*args, **kwargs)

    def calcular_subtotal(self):
        return sum(concepto.monto for concepto in self.conceptos.all())

    def calcular_iva(self):
        return self.subtotal * Decimal('0.16')

    def calcular_total(self):
        return self.subtotal + self.iva

    def __str__(self):
        tipo = "Débito" if self.es_debito else "Crédito"
        return f"Nota de {tipo} {self.numero_nota} - {self.nombre_cliente} - {self.fecha_emision}"

class Concepto(models.Model):
    nota = models.ForeignKey('Nota', related_name='conceptos', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion}: {self.monto}"



