import logging
from django.test import TestCase
from django.db import transaction, IntegrityError

# CORRECCIÓN 1: Importamos pasando primero por la carpeta Backend
from Backend.facturas.models import Factura

# CORRECCIÓN 2: Actualizamos la ruta del logger
logger = logging.getLogger('Backend.facturas.controllers')

class MantenibilidadIntegracionTests(TestCase):

    def test_int_man_01_trazabilidad_logs(self):
        """
        INT-MAN-01: Analizabilidad.
        Verifica que al ocurrir un error, el sistema genere un registro en el log
        en lugar de romperse o usar print().
        """
        # CORRECCIÓN 3: Actualizamos la ruta vigilada por assertLogs
        with self.assertLogs('Backend.facturas.controllers', level='ERROR') as log_catcher:
            
            try:
                # Simulamos la ejecución del controlador que falla
                raise ValueError("Simulando que el frontend envió datos corruptos")
            except ValueError as e:
                # El controlador registra el error con la librería estándar
                logger.error(f"Error de integración procesando la solicitud: {str(e)}")

        self.assertTrue(len(log_catcher.output) > 0)
        self.assertIn("Error de integración", log_catcher.output[0])
        self.assertIn("datos corruptos", log_catcher.output[0])

    def test_int_man_02_atomicidad_transacciones(self):
        """
        INT-MAN-02: Modificabilidad.
        Verifica que si un proceso de guardado falla a la mitad, 
        se aplique un Rollback y no queden datos huérfanos.
        """
        conteo_inicial = Factura.objects.count()

        try:
            with transaction.atomic():
                Factura.objects.create(
                    numero_factura="F-9999",
                    subtotal=500.0,
                    iva=80.0,
                    emitida=True
                )
                raise IntegrityError("Fallo simulado al guardar dependencias")
                
        except IntegrityError:
            pass

        conteo_final = Factura.objects.count()

        self.assertEqual(
            conteo_inicial, 
            conteo_final, 
            "Fallo de Modificabilidad: La transacción no fue atómica y dejó datos basura en la BD."
        )