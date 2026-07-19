"""
tests/test_b1_validador_rif.py

Bloque B1 — Validador de Identidad Fiscal (RIF/Cédula)
Componente: validar_cedula_rif() — CONFIRMADO: existen 2 copias byte-a-byte
idénticas, una en facturas/models.py (sí se usa, como validators=[] del
campo Factura.cedula_cliente) y otra en notas_de_debito_credito/models.py
(NO se usa en ningún campo de Nota -> código muerto).
Casos: UT-B1-01 a UT-B1-05 (5 casos)

Corresponde a CP-02 (formato SENIAT) y CP-04 (duplicación del validador).

Prefijos reales confirmados (con conteo exacto de dígitos, vía código
fuente): J-XXXXXXXXX (9), V-XXXXXXXX (8), E-XXXXXXXX (8), P-XXXXXXXXX (9),
G-XXXXXXXXX (9). El prefijo P (Pasaporte) no estaba contemplado en la
versión anterior de este plan.
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from Backend.facturas.models import validar_cedula_rif as validar_cedula_rif_factura
from Backend.notas_de_debito_credito.models import validar_cedula_rif as validar_cedula_rif_notas


class ValidadorRifFacturaTest(TestCase):
    """UT-B1-01 a UT-B1-04 — la copia realmente usada, en facturas/models.py."""

    def test_UT_B1_01_acepta_los_5_prefijos_validos_seniat(self):
        for valor in ["J-123456789", "V-12345678", "E-12345678", "P-123456789", "G-123456789"]:
            with self.subTest(valor=valor):
                try:
                    validar_cedula_rif_factura(valor)
                except ValidationError:
                    self.fail(f"'{valor}' debería ser aceptado y lanzó ValidationError")

    def test_UT_B1_02_rechaza_cadena_sin_prefijo(self):
        with self.assertRaises(ValidationError):
            validar_cedula_rif_factura("12345678")

    def test_UT_B1_03_borde_prefijo_en_minuscula(self):
        with self.assertRaises(ValidationError):
            validar_cedula_rif_factura("v-12345678")

    def test_UT_B1_04_borde_cantidad_de_digitos_incorrecta(self):
        """El patrón exige un conteo EXACTO de dígitos por prefijo (no un rango)."""
        casos_invalidos = [
            "J-123",           # muy corto para J (exige 9)
            "V-123456789",     # un dígito de más para V (exige exactamente 8)
        ]
        for valor in casos_invalidos:
            with self.subTest(valor=valor):
                with self.assertRaises(ValidationError):
                    validar_cedula_rif_factura(valor)

    def test_UT_B1_05_regresion_ambas_copias_siguen_siendo_identicas(self):
        """
        CP-04: hoy las 2 copias son byte-a-byte idénticas. Este caso es un
        guardarraíl de regresión: si alguien corrige una copia sin corregir
        la otra (el riesgo real de mantener código duplicado), este test
        debe empezar a fallar y delatarlo.
        """
        validos = ["J-123456789", "V-12345678", "P-123456789"]
        invalidos = ["ABC", "J-12", "v-12345678"]

        for valor in validos + invalidos:
            with self.subTest(valor=valor):
                resultado_facturas = self._pasa(validar_cedula_rif_factura, valor)
                resultado_notas = self._pasa(validar_cedula_rif_notas, valor)
                self.assertEqual(resultado_facturas, resultado_notas,
                                  f"Las dos copias divergen para '{valor}'")

    @staticmethod
    def _pasa(validador, valor):
        try:
            validador(valor)
            return True
        except ValidationError:
            return False
