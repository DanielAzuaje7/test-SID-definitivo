"""
tests/test_b3_numeracion.py

Bloque B3 — Numeración y Trazabilidad
Casos: UT-B3-01 a UT-B3-05 (5 casos)

Corresponde a CP-05 (correlativo de Factura) y CP-06 (prefijo por tipo
de documento).

IMPORTANTE (confirmado con código real, corrige un supuesto anterior):
UT-B3-05 originalmente asumía que Factura.save() protegía contra un
numero_factura forzado manualmente. El código real hace lo CONTRARIO:
`if not self.numero_factura:` — si ya tiene un valor (aunque sea
inválido o repetido), save() lo respeta tal cual, sin generar ni
validar nada. Es una falla de integridad real, no protegida por el
sistema. UT-B3-05 ahora documenta este comportamiento tal como es,
igual que UT-B4-03 documenta la inconsistencia de fechas.
"""
import re
from django.test import TestCase

from tests.unitarias._fixtures import crear_factura, crear_usuario, crear_nota, crear_orden


class NumeracionFacturaTest(TestCase):

    def test_UT_B3_01_correlativo_unico_entre_dos_facturas_seguidas(self):
        usuario = crear_usuario()
        factura_1 = crear_factura(usuario=usuario)
        factura_2 = crear_factura(usuario=usuario)

        for factura in (factura_1, factura_2):
            with self.subTest(numero=factura.numero_factura):
                self.assertRegex(factura.numero_factura, r"^F-\d{5}$")

        self.assertNotEqual(factura_1.numero_factura, factura_2.numero_factura)

    def test_UT_B3_05_borde_numero_factura_forzado_no_se_valida(self):
        """
        CONFIRMADO por código real: un numero_factura asignado a mano ANTES
        de guardar se conserva tal cual (save() solo genera uno si el campo
        está vacío). No hay validación de formato ni chequeo de colisión
        para este camino. Documenta el hallazgo, no lo corrige.
        """
        usuario = crear_usuario()
        factura = crear_factura(usuario=usuario, numero_factura="NUM-FORZADO-INVALIDO")
        self.assertEqual(factura.numero_factura, "NUM-FORZADO-INVALIDO")
        self.assertNotRegex(factura.numero_factura, r"^F-\d{5}$")


class NumeracionNotaYOrdenTest(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.factura = crear_factura(usuario=self.usuario)

    def test_UT_B3_02_prefijo_nota_de_debito(self):
        nota = crear_nota(self.factura, usuario=self.usuario, es_debito=True)
        self.assertRegex(nota.numero_nota, r"^ND-\d{5}$")

    def test_UT_B3_03_prefijo_nota_de_credito(self):
        nota = crear_nota(self.factura, usuario=self.usuario, es_debito=False)
        self.assertRegex(nota.numero_nota, r"^NC-\d{5}$")

    def test_UT_B3_04_prefijo_orden_de_entrega(self):
        orden = crear_orden(self.factura, usuario=self.usuario)
        self.assertRegex(orden.numero_orden_entrega, r"^OE-\d{5}$")
