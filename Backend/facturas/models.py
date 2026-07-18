from django.db import models
from django.utils import timezone
from django.conf import settings
import re
from django.core.exceptions import ValidationError
from decimal import Decimal     

def validar_cedula_rif(valor):
    patron = r'^(J-\d{9}|V-\d{8}|E-\d{8}|P-\d{9}|G-\d{9})$'
    if not re.match(patron, valor):
        raise ValidationError(
            'El RIF/Cédula debe tener el formato J-XXXXXXXXX, V-XXXXXXXX, E-XXXXXXXX, P-XXXXXXXXX o G-XXXXXXXXX.'
        )


def validar_fecha_emision(valor):
    if valor > timezone.now().date():
        raise ValidationError('La fecha de emisión no puede ser en el futuro.')


class Factura(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    lugar_emision = models.CharField(max_length=100)
    fecha_emision = models.DateField(validators=[validar_fecha_emision])
    telefono_cliente = models.CharField(max_length=20)
    cedula_cliente = models.CharField(max_length=12, validators=[validar_cedula_rif])
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_factura = models.CharField(max_length=20, unique=True, blank=True, null=True)
    emitida = models.BooleanField(default=False)

    def calcular_totales(self):
        subtotal = sum([p.cantidad * p.precio_unitario for p in self.productos.all()])
        iva = subtotal * Decimal('0.16') 
        total = subtotal + iva
        self.subtotal = subtotal
        self.iva = iva
        self.total = total

    def emitir_factura(self):
        self.emitida = True

    def save(self, *args, **kwargs): 
        is_new = self.pk is None
        self.fecha_emision = timezone.now()
        if not self.numero_factura:
            count = Factura.objects.filter(usuario=self.usuario).count() + 1
            while True:
                numero = f"F-{count:05d}"
                if not Factura.objects.filter(numero_factura=numero).exists():
                    self.numero_factura = numero
                    break
                count += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura #{self.id} - {self.nombre_cliente}"

class ProductoFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name='productos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} (x{self.cantidad})"
