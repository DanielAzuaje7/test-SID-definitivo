import os
import time
import subprocess
import sys
import urllib.request
from urllib.error import HTTPError
from pathlib import Path 

def test_modularidad_feature_flag():
    root_dir = Path(__file__).resolve().parent.parent.parent 
    os.chdir(root_dir) 

    env_path = ".env"
    puerto = 8005

    print("--- INICIANDO AUDITORÍA MNT-SYS-04 (Modularidad y Aislamiento) ---")

    lineas_env_original = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lineas_env_original = f.readlines()

    servidor = None

    try:
        print("\n🚩 1. Apagando módulo de Notas vía Feature Flag...")
        with open(env_path, "w", encoding="utf-8") as f:
            for linea in lineas_env_original:
                if not linea.startswith("ACTIVAR_NOTAS="):
                    f.write(linea)
            f.write("ACTIVAR_NOTAS=False\n") 

        # 🌟 EL ARREGLO: Forzamos la variable en la memoria del subproceso
        env_subproceso = os.environ.copy()
        env_subproceso["ACTIVAR_NOTAS"] = "False"

        print(f"⏳ 2. Levantando servidor en puerto {puerto}...")
        servidor = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", str(puerto), "--settings=imprenta_digital.settings_sistema", "--noreload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env_subproceso # <- PASAMOS EL ENTORNO
        )
        time.sleep(5) 

        print("\n📡 3. Evaluando módulo apagado (Notas)...")
        estado_notas = 0
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{puerto}/notas/", timeout=5)
            estado_notas = 200
        except HTTPError as e:
            estado_notas = e.code
        except Exception as err:
            estado_notas = 500

        print("🛡️ 4. Evaluando supervivencia del sistema (Facturas)...")
        estado_facturas = 0
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{puerto}/crear-factura/", timeout=5)
            estado_facturas = 200
        except HTTPError as e:
            estado_facturas = e.code
        except Exception as err:
            estado_facturas = 500

        print("\n🧠 Analizando resultados de Modularidad...")
        if estado_notas == 404 and estado_facturas < 400:
            print(f"🎉 ¡PRUEBA EXITOSA!")
            print(f"   - Módulo Notas: HTTP {estado_notas} (Aislado correctamente)")
            print(f"   - Módulo Facturas: HTTP {estado_facturas} (Sobrevivió y está operativo)")
            print("📈 Diagnóstico: Nivel de Modularidad ALTO.")
        else:
            error_msg = (
                "FALLO: El sistema colapsó o no aisló correctamente los módulos.\n"
                f"   - Módulo Notas arrojó: HTTP {estado_notas}\n"
                f"   - Módulo Facturas arrojó: HTTP {estado_facturas}"
            )
            assert False, error_msg

    finally:
        print("\n🔌 6. Apagando servidor y restaurando entorno...")
        if servidor and servidor.poll() is None:
            servidor.terminate()
            servidor.wait()
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lineas_env_original)

if __name__ == "__main__":
    test_modularidad_feature_flag()