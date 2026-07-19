"""
tests/test_b5_herencia_cliente.py

Bloque B5 — Herencia de Datos del Cliente en Nota/OrdenDeEntrega
Casos: UT-B5-01 a UT-B5-03 (3 casos)

Corresponde a CP-08: Nota y OrdenDeEntrega no heredan de una clase base
común, así que copian a mano los datos del cliente desde la Factura
(factura_afectada) dentro de su propio save().

Campos reales confirmados: nombre_cliente, telefono_cliente,
cedula_cliente, lugar_emision (los 4 se copian en ambos modelos).
OrdenDeEntrega NO copia fecha_emision de la factura (usa su propio
timezone.now()); por eso este bloque no compara fecha_emision.
"""
from django.test import TestCase

from tests.unitarias._fixtures import crear_factura, crear_usuario, crear_nota, crear_orden


class HerenciaDatosClienteTest(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.factura = crear_factura(
            usuario=self.usuario,
            nombre_cliente="Ana Pérez",
            cedula_cliente="V-12345678",
            telefono_cliente="0212-1234567",
            lugar_emision="Caracas",
        )

    def _assert_datos_cliente_iguales(self, destino):
        self.assertEqual(destino.nombre_cliente, self.factura.nombre_cliente)
        self.assertEqual(destino.telefono_cliente, self.factura.telefono_cliente)
        self.assertEqual(destino.cedula_cliente, self.factura.cedula_cliente)
        self.assertEqual(destino.lugar_emision, self.factura.lugar_emision)

    def test_UT_B5_01_nota_copia_datos_del_cliente(self):
        nota = crear_nota(self.factura, usuario=self.usuario, es_debito=True)
        self._assert_datos_cliente_iguales(nota)

    def test_UT_B5_02_orden_de_entrega_copia_datos_del_cliente(self):
        orden = crear_orden(self.factura, usuario=self.usuario)
        self._assert_datos_cliente_iguales(orden)

    def test_UT_B5_03_borde_la_copia_no_se_actualiza_retroactivamente(self):
        """
        Si luego se cambia el dato en la factura original y NO se vuelve
        a guardar la nota, la nota conserva el valor copiado en su
        momento — confirma que es una copia de datos, no una referencia
        viva a la factura.
        """
        nota = crear_nota(self.factura, usuario=self.usuario, es_debito=True)

        self.factura.nombre_cliente = "Otro Nombre"
        self.factura.save()

        nota.refresh_from_db()
        self.assertEqual(nota.nombre_cliente, "Ana Pérez")
        self.assertNotEqual(nota.nombre_cliente, self.factura.nombre_cliente)
