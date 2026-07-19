"""
tests/test_b2_iva_consistencia.py

Bloque B2 — Consistencia de IVA entre Módulos
Casos: UT-B2-01 a UT-B2-03 (3 casos)

Corresponde a CP-03, confirmado explícitamente en la documentación del
proyecto: "El cálculo del IVA al 16% está hardcodeado en los 3 módulos
(facturas, notas, órdenes)."

IMPORTANTE (confirmado con código real, corrige un supuesto anterior):
los 3 módulos NO comparten una firma de método uniforme:
- Factura: el IVA se calcula DENTRO de calcular_totales() (no hay un
  calcular_iva() independiente); toma el subtotal de sus ProductoFactura.
- Nota y OrdenDeEntrega: sí tienen calcular_iva(self) como método propio,
  pero SIN parámetro — leen self.subtotal (debe estar ya asignado).
Por eso cada caso invoca el mecanismo real de cada modelo en vez de una
firma común inventada.

Ninguno de los 3 redondea (ninguno hace .quantize()) — ver también B0.
"""
from decimal import Decimal
from django.test import TestCase

from tests.unitarias._fixtures import crear_factura, agregar_productos, crear_nota, crear_orden
from Backend.notas_de_debito_credito.models import Nota
from Backend.orden_de_entrega.models import OrdenDeEntrega


class ConsistenciaIvaTest(TestCase):

    def _iva_factura(self, subtotal):
        factura = crear_factura()
        agregar_productos(factura, (subtotal, 1))
        factura.calcular_totales()
        return factura.iva

    def _iva_nota_o_orden(self, modelo, subtotal):
        instancia = modelo()
        instancia.subtotal = Decimal(str(subtotal))
        return instancia.calcular_iva()

    def test_UT_B2_01_mismo_subtotal_en_los_tres_modulos(self):
        resultados = {
            "Factura": self._iva_factura(500.00),
            "Nota": self._iva_nota_o_orden(Nota, 500.00),
            "OrdenDeEntrega": self._iva_nota_o_orden(OrdenDeEntrega, 500.00),
        }
        for modulo, iva in resultados.items():
            with self.subTest(modulo=modulo):
                self.assertEqual(iva, Decimal("80.00"))

    def test_UT_B2_02_borde_subtotal_en_cero(self):
        resultados = {
            "Factura": self._iva_factura(0.00),
            "Nota": self._iva_nota_o_orden(Nota, 0.00),
            "OrdenDeEntrega": self._iva_nota_o_orden(OrdenDeEntrega, 0.00),
        }
        for modulo, iva in resultados.items():
            with self.subTest(modulo=modulo):
                self.assertEqual(iva, Decimal("0.00"))

    def test_UT_B2_03_borde_decimales_consistentes_sin_redondear(self):
        """
        Ninguno de los 3 redondea (confirmado): deben coincidir en el
        MISMO valor crudo sin redondear (53.3328), no en 53.33. Si algún
        módulo agregara .quantize() y los otros no, este caso lo detecta.
        """
        resultados = {
            "Factura": self._iva_factura(333.33),
            "Nota": self._iva_nota_o_orden(Nota, 333.33),
            "OrdenDeEntrega": self._iva_nota_o_orden(OrdenDeEntrega, 333.33),
        }
        for modulo, iva in resultados.items():
            with self.subTest(modulo=modulo):
                self.assertEqual(iva, Decimal("53.3328"))
