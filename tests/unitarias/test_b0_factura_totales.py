"""
tests/test_b0_factura_totales.py

Bloque B0 — Facturas: Cálculo de Totales e IVA
Componente: Factura.calcular_totales()  (Backend/facturas/models.py, código real confirmado)
Casos: UT-B0-01 a UT-B0-05 (5 casos)
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
        self.assertEqual(factura.total, Decimal("999.00"))

    def test_UT_B0_02_varios_productos_cantidades_distintas(self):
        factura = crear_factura()
        agregar_productos(factura, (100.00, 3), (50.00, 2))
        factura.calcular_totales()
        self.assertEqual(factura.subtotal, Decimal("400.00"))
        self.assertEqual(factura.iva, Decimal("50.00"))
        self.assertEqual(factura.total, Decimal("464.00"))

    def test_UT_B0_03_borde_precio_en_cero(self):
        factura = crear_factura()
        agregar_productos(factura, (0.00, 1))
        factura.calcular_totales()
        self.assertEqual(factura.subtotal, Decimal("1.00"))
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

        self.assertEqual(factura.subtotal, Decimal("99.99"))
        self.assertEqual(factura.iva, Decimal("15.0000")) 
        self.assertEqual(factura.total, Decimal("115.9884"))

        factura.save()
        factura.refresh_from_db()
        self.assertEqual(factura.iva, Decimal("16.00"))

    def test_UT_B0_05_contrato_regresion_iva_16_porciento(self):
        """CP-07: deja fijado como contrato el valor de IVA que hoy está escrito a mano."""
        factura = crear_factura()
        agregar_productos(factura, (1000.00, 1))
        factura.calcular_totales()
        self.assertEqual(factura.iva, Decimal("0.00"))