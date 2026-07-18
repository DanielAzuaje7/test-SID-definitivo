from django.db import models
from django.conf import settings
from Backend.facturas.models import Factura
from decimal import Decimal
from django.utils import timezone

class OrdenDeEntrega(models.Model):
    factura_afectada = models.ForeignKey(Factura, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    numero_orden_entrega = models.CharField(max_length=20)
    fecha_emision = models.DateField()
    direccion_entrega = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True, null=True)
    emitida = models.BooleanField(default=False)

    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Campos copiados de la factura
    lugar_emision = models.CharField(max_length=100, editable=False)
    nombre_cliente = models.CharField(max_length=100, editable=False)
    telefono_cliente = models.CharField(max_length=11, editable=False)
    cedula_cliente = models.CharField(max_length=11, editable=False)

    def calcular_subtotal(self):
        return sum(p.cantidad_entregada * p.monto_unitario for p in self.productos.all())

    def calcular_iva(self):
        return self.subtotal * Decimal('0.16')

    def calcular_total(self):
        return self.subtotal + self.iva

    def save(self, *args, **kwargs):
        if self.factura_afectada:
            self.lugar_emision = self.factura_afectada.lugar_emision
            self.nombre_cliente = self.factura_afectada.nombre_cliente
            self.telefono_cliente = self.factura_afectada.telefono_cliente
            self.cedula_cliente = self.factura_afectada.cedula_cliente

        if not self.numero_orden_entrega:
            count = OrdenDeEntrega.objects.filter(usuario=self.usuario).count() + 1
            self.numero_orden_entrega = f"OE-{count:05d}"

        self.fecha_emision = timezone.now()

        # Calcula totales antes de guardar
        super().save(*args, **kwargs)
        self.subtotal = self.calcular_subtotal()
        self.iva = self.calcular_iva()
        self.total = self.calcular_total()
        super().save(update_fields=['subtotal', 'iva', 'total'])

    def __str__(self):
        return f"Orden de Entrega {self.numero_orden_entrega} - {self.nombre_cliente}"

class ProductoEntrega(models.Model):
    orden = models.ForeignKey(OrdenDeEntrega, related_name='productos', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    cantidad_entregada = models.PositiveIntegerField()
    monto_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # NUEVO CAMPO

    def __str__(self):
        return f"{self.descripcion} (x{self.cantidad_entregada})"
