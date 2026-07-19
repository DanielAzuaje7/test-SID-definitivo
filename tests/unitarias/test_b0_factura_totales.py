"""
tests/test_b0_factura_totales.py

Bloque B0 — Facturas: Cálculo de Totales e IVA
Componente: Factura.calcular_totales()  (Backend/facturas/models.py, código real confirmado)
Casos: UT-B0-01 a UT-B0-05 (5 casos)

Corresponde a CP-01 (modularidad del cálculo) y CP-07 (contrato de
regresión: la tasa de IVA del 16% sigue escrita a mano en el código).

IMPORTANTE (confirmado con código fuente real, corrige un supuesto anterior):
calcular_totales() NO redondea nada — hace `iva = subtotal * Decimal('0.16')`
sin `.quantize()`. El valor queda con precisión completa en memoria
(ej. 15.9984, no 16.00). El redondeo a 2 decimales solo ocurre cuando
Django persiste el DecimalField(10,2) en la base de datos. UT-B0-04 prueba
las dos cosas por separado para dejar esto documentado.
"""
from decimal import Decimal
from django.test import TestCase

from tests.unitarias._fixtures import crear_factura, agregar_productos


class FacturaCalcularTotalesTest(TestCase):

    def test_UT_B0_01_un_producto_cantidad_1(self):
        factura = crear_factura()
        agregar_productos(factura, (250.00, 1))
        factura.calcular_totales()
        self.assertEqual(factura.subtotal, Decimal("250.00"))
        self.assertEqual(factura.iva, Decimal("40.00"))
        self.assertEqual(factura.total, Decimal("290.00"))

    def test_UT_B0_02_varios_productos_cantidades_distintas(self):
        factura = crear_factura()
        agregar_productos(factura, (100.00, 3), (50.00, 2))
        factura.calcular_totales()
        self.assertEqual(factura.subtotal, Decimal("400.00"))
        self.assertEqual(factura.iva, Decimal("64.00"))
        self.assertEqual(factura.total, Decimal("464.00"))

    def test_UT_B0_03_borde_precio_en_cero(self):
        factura = crear_factura()
        agregar_productos(factura, (0.00, 1))
        factura.calcular_totales()
        self.assertEqual(factura.subtotal, Decimal("0.00"))
        self.assertEqual(factura.iva, Decimal("0.00"))
        self.assertEqual(factura.total, Decimal("0.00"))

    def test_UT_B0_04_borde_decimales_calcular_totales_no_redondea(self):
        """
        CONFIRMADO por código real: calcular_totales() no hace quantize().
        El valor en memoria queda con precisión completa; solo al guardar
        y releer de la BD se ve el redondeo a 2 decimales del DecimalField.
        """
        factura = crear_factura()
        agregar_productos(factura, (33.33, 3))
        factura.calcular_totales()

        # En memoria, justo después de calcular_totales(): SIN redondear
        self.assertEqual(factura.subtotal, Decimal("99.99"))
        self.assertEqual(factura.iva, Decimal("15.9984"))  # 99.99 * 0.16, sin quantize
        self.assertEqual(factura.total, Decimal("115.9884"))

        # Al guardar y releer de la BD: el DecimalField(10,2) sí redondea
        factura.save()
        factura.refresh_from_db()
        self.assertEqual(factura.iva, Decimal("16.00"))

    def test_UT_B0_05_contrato_regresion_iva_16_porciento(self):
        """CP-07: deja fijado como contrato el valor de IVA que hoy está escrito a mano."""
        factura = crear_factura()
        agregar_productos(factura, (1000.00, 1))
        factura.calcular_totales()
        self.assertEqual(factura.iva, Decimal("160.00"))
