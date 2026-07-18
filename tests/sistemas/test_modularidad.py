import os
import time
import subprocess
import sys
import urllib.request
from urllib.error import HTTPError
from pathlib import Path # Añadimos pathlib

def test_modularidad_feature_flag():
    # --- ENCONTRAR LA RAÍZ DEL PROYECTO ---
    # Sube 3 niveles: test_modularidad.py -> sistemas -> test -> raíz
    root_dir = Path(__file__).resolve().parent.parent.parent 
    os.chdir(root_dir) # Nos ubicamos en la raíz para hallar manage.py y .env
    # --------------------------------------

    env_path = ".env"
    puerto = 8005

    print("--- INICIANDO AUDITORÍA MNT-SYS-04 (Modularidad y Aislamiento) ---")

    # 1. APAGAR EL MÓDULO DE NOTAS DESDE AFUERA
    print("\n🚩 1. Apagando módulo de Notas vía Feature Flag...")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("DB_NAME=db.sqlite3\n")
        # Mantenemos DEBUG en True para que Django local no colapse por falta de estáticos
        f.write("DEBUG_MODE=True\n") 
        f.write("ACTIVAR_NOTAS=False\n") # ¡Interruptor apagado!

    # 2. LEVANTAR EL SERVIDOR
    print(f"⏳ 2. Levantando servidor en puerto {puerto}...")
    servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", str(puerto), "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5) # Esperamos que Django despierte

    # 3. PRUEBA DE AISLAMIENTO (El módulo apagado)
    print("\n📡 3. Evaluando módulo apagado (Notas)...")
    estado_notas = 0
    try:
        # Asegúrate de que esta sea una ruta válida cuando el módulo está activo
        urllib.request.urlopen(f"http://127.0.0.1:{puerto}/notas/", timeout=5)
        estado_notas = 200
    except HTTPError as e:
        estado_notas = e.code
    except Exception as err:
        estado_notas = 500

    # 4. PRUEBA DE SUPERVIVENCIA (El resto del sistema)
    print("🛡️ 4. Evaluando supervivencia del sistema (Facturas)...")
    estado_facturas = 0
    try:
        # Asegúrate de que esta ruta sea válida
        urllib.request.urlopen(f"http://127.0.0.1:{puerto}/crear-factura/", timeout=5)
        estado_facturas = 200
    except HTTPError as e:
        estado_facturas = e.code
    except Exception as err:
        estado_facturas = 500

    # 5. APAGAR Y RESTAURAR
    print("\n🔌 5. Apagando servidor y restaurando entorno...")
    servidor.kill()
    time.sleep(2)
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("DB_NAME=db.sqlite3\n")
        f.write("DEBUG_MODE=True\n")
        # El settings asumirá ACTIVAR_NOTAS=True por defecto.

    # 6. VALIDACIÓN MATEMÁTICA
    print("\n🧠 Analizando resultados de Modularidad...")
    
    # 404 significa que la ruta desapareció con éxito.
    # Aceptamos 200 (OK) o códigos 300 (Redirecciones al Login) como válidos para Facturas.
    if estado_notas == 404 and estado_facturas < 400:
        print(f"🎉 ¡PRUEBA EXITOSA!")
        print(f"   - Módulo Notas: HTTP {estado_notas} (Aislado correctamente)")
        print(f"   - Módulo Facturas: HTTP {estado_facturas} (Sobrevivió y está operativo)")
        print("📈 Diagnóstico: Nivel de Modularidad ALTO. Los módulos están desacoplados a nivel de enrutamiento.")
    else:
        print("❌ FALLO: El sistema colapsó o no aisló correctamente los módulos.")
        print(f"   - Módulo Notas arrojó: HTTP {estado_notas}")
        print(f"   - Módulo Facturas arrojó: HTTP {estado_facturas}")

if __name__ == "__main__":
    test_modularidad_feature_flag()