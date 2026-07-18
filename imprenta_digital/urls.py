"""
URL configuration for imprenta_digital project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- Importamos los settings para leer el interruptor

urlpatterns = [
    path('admin/', admin.site.urls),

    # paths de la aplicacion core
    path('', include('Backend.core.urls')), 

    # paths de facturas 
    path('', include('Backend.facturas.urls')),

    # paths de usuarios
    path('', include('Backend.usuarios.urls')),
    
    # paths de las ordenes de entrega
    path('', include('Backend.orden_de_entrega.urls')), 
]

# --- ESCUDO DE MODULARIDAD (MNT-SYS-04) ---
# Solo acopla las rutas de las notas si el interruptor está activado en el .env
if settings.MODULO_NOTAS_ACTIVO:
    urlpatterns.append(path('', include('Backend.notas_de_debito_credito.urls')))