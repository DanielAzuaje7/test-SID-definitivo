# imprenta_digital/settings_sistema.py

# 1. Importamos TODA la configuración del settings original
from .settings import *
import os
from dotenv import load_dotenv

# 2. Cargamos las variables de entorno para las pruebas
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 3. Sobrescribimos SOLO lo que necesitamos modificar para Sistemas
DEBUG = os.getenv('DEBUG_MODE', 'False') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

MODULO_NOTAS_ACTIVO = os.getenv('ACTIVAR_NOTAS', 'True') == 'True'

# Redirigimos la base de datos a lo que diga el .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
    }
}

# 4. Agregamos el sistema de Logs para la prueba MNT-SYS-01
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',  # <-- CLAVE: Bajar a INFO para que atrape el tráfico
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'auditoria_sid.log',
        },
    },
    'loggers': {
        # ESTE es el canal secreto que usa runserver para imprimir "GET /ruta 404"
        'django.server': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Mantenemos este por si ocurren errores críticos internos (500)
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}