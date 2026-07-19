"""
tests/_fixtures.py

Helpers compartidos por los 6 bloques de prueba (UT-B0 a UT-B5) del
Plan de Pruebas Unitarias — SID, Equipo 3.

Construido a partir de código FUENTE REAL confirmado (no supuestos):
facturas/models.py y orden_de_entrega/models.py fueron citados literalmente;
notas_de_debito_credito/models.py se reconstruyó a partir de las fórmulas
explícitas documentadas (calcular_subtotal/calcular_iva/calcular_total) y
del mismo patrón de save() ya confirmado en los otros dos módulos.

Campos reales confirmados (no eran los que se habían asumido antes):
- No existe un modelo Usuario custom: se usa django.contrib.auth.models.User.
- Factura: nombre_cliente, lugar_emision, fecha_emision, telefono_cliente,
  cedula_cliente (NO "cedula_rif_cliente"), usuario, subtotal, iva, total,
  numero_factura (NO "numero_control"), emitida.
- Los productos de una Factura son un modelo real (ProductoFactura) vía FK
  related_name="productos" — no una lista en memoria. La Factura debe
  guardarse primero para poder agregarle productos.
"""
from decimal import Decimal

from django.contrib.auth.models import User

from Backend.facturas.models import Factura, ProductoFactura
from Backend.notas_de_debito_credito.models import Nota
from Backend.orden_de_entrega.models import OrdenDeEntrega


def crear_usuario(**overrides):
    datos = {"username": f"user_{User.objects.count()+1}", "password": "clave-temporal-123"}
    datos.update(overrides)
    return User.objects.create_user(**datos)


def datos_cliente_default(**overrides):
    """Datos de cliente reutilizados por Factura y, por copia, por Nota/OrdenDeEntrega."""
    datos = {
        "nombre_cliente": "Ana Pérez",
        "cedula_cliente": "V-12345678",
        "telefono_cliente": "0212-1234567",
        "lugar_emision": "Caracas",
    }
    datos.update(overrides)
    return datos


def crear_factura(usuario=None, **overrides):
    """
    Crea y GUARDA una Factura (se guarda siempre: ProductoFactura necesita
    el FK a una Factura con PK real, y Factura.save() es quien genera
    numero_factura y fecha_emision).
    """
    usuario = usuario or crear_usuario()
    datos = datos_cliente_default()
    datos.update(overrides)
    factura = Factura(usuario=usuario, **datos)
    factura.save()
    return factura


def agregar_productos(factura, *pares_precio_cantidad):
    """agregar_productos(factura, (250.00, 1), (100.00, 3)) -> crea ProductoFactura reales."""
    productos = []
    for precio, cantidad in pares_precio_cantidad:
        productos.append(ProductoFactura.objects.create(
            factura=factura, nombre="Producto de prueba",
            cantidad=cantidad, precio_unitario=Decimal(str(precio)),
        ))
    return productos


def crear_nota(factura, usuario, es_debito=True):
    nota = Nota(
        factura_afectada=factura,
        usuario=usuario,
        es_debito=es_debito,
        subtotal=100.00,  # <-- Agrega esto
        iva=16.00,        # <-- Agrega esto
        total=116.00      # <-- Agrega esto
    )
    nota.save()
    return nota


def crear_orden(factura_afectada, usuario=None, **overrides):
    usuario = usuario or factura_afectada.usuario
    orden = OrdenDeEntrega(
        factura_afectada=factura_afectada, usuario=usuario,
        direccion_entrega=overrides.pop("direccion_entrega", "Av. Principal, Caracas"),
        **overrides,
    )
    orden.save()
    return orden
