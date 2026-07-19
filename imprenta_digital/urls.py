"""
URL configuration for imprenta_digital project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- Importamos los settings

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

# --- ESCUDO DE MODULARIDAD (Tolerante a fallos) ---
# getattr busca la variable. Si el settings original no la tiene, asume True por defecto
# y carga las rutas normalmente para el resto del equipo.
if getattr(settings, 'MODULO_NOTAS_ACTIVO', True):
    urlpatterns.append(path('', include('Backend.notas_de_debito_credito.urls')))