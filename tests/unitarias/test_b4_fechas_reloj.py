"""
tests/test_b4_fechas_reloj.py

Bloque B4 — Validación de Fechas y Dependencia del Reloj
Casos: UT-B4-01 a UT-B4-04 (4 casos)

Corresponde a CP-09 (el guardado ignora la validación de fecha futura) y
CP-10 (Factura.save() depende del reloj del sistema).

IMPORTANTE (confirmado con código real, corrige un supuesto anterior):
Factura.save() hace `self.fecha_emision = timezone.now()`, que es un
datetime completo (con hora), NO una fecha. En memoria, justo después de
save(), factura.fecha_emision es un datetime; solo se vuelve un date
"limpio" tras factura.refresh_from_db() (Django lo trunca al guardar el
DateField en la BD). Por eso estos casos usan refresh_from_db() antes de
comparar contra una fecha.

Nota adicional (encontrada al validar estos tests): con USE_TZ=True,
Django localiza el datetime a settings.TIME_ZONE antes de truncarlo a
date() al guardar un DateField. `timezone.now().date()` a secas usa UTC
directo, así que puede diferir en 1 día del valor ya persistido cerca
de medianoche. Por eso las comparaciones usan
`timezone.localtime(...).date()`.

validar_fecha_emision() vive en el mismo archivo que validar_cedula_rif
(facturas/models.py), no en un módulo "validators.py" aparte como se
había asumido antes.
"""
import datetime
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from Backend.facturas.models import validar_fecha_emision
from tests.unitarias._fixtures import crear_factura, crear_usuario


class ValidarFechaEmisionTest(TestCase):

    def test_UT_B4_01_rechaza_fecha_futura(self):
        fecha_futura = timezone.now().date() + datetime.timedelta(days=5)
        with self.assertRaises(ValidationError):
            validar_fecha_emision(fecha_futura)

    def test_UT_B4_02_acepta_fecha_de_hoy(self):
        hoy = timezone.now().date()
        try:
            validar_fecha_emision(hoy)
        except ValidationError:
            self.fail("La fecha de hoy no debería lanzar ValidationError")


class FacturaSaveFechaTest(TestCase):

    def test_UT_B4_03_guardado_siempre_usa_la_fecha_actual(self):
        """
        CP-09: sin importar qué fecha se intente asignar (pasada o
        futura), save() la sobreescribe siempre con el momento actual.
        La validación de fecha futura, aunque existe como función, no
        protege este campo en la práctica.
        """
        usuario = crear_usuario()
        fecha_futura = timezone.now().date() + datetime.timedelta(days=5)
        factura = crear_factura(usuario=usuario, fecha_emision=fecha_futura)

        factura.refresh_from_db()
        # Django localiza a settings.TIME_ZONE antes de truncar a date() al
        # guardar un DateField; hay que comparar con esa misma referencia
        # (con USE_TZ=True, timezone.now().date() a secas usa UTC y puede
        # diferir en 1 día del date() ya localizado que quedó en la BD).
        self.assertEqual(factura.fecha_emision, timezone.localtime(timezone.now()).date())
        self.assertNotEqual(factura.fecha_emision, fecha_futura)

    def test_UT_B4_04_depende_del_reloj_del_sistema(self):
        """
        CP-10: la única forma confiable de probar la fecha guardada es
        sustituyendo el reloj del sistema.
        """
        fecha_simulada = datetime.datetime(2025, 1, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)

        with patch("django.utils.timezone.now", return_value=fecha_simulada):
            usuario = crear_usuario()
            factura = crear_factura(usuario=usuario)

        factura.refresh_from_db()
        self.assertEqual(factura.fecha_emision, timezone.localtime(fecha_simulada).date())
