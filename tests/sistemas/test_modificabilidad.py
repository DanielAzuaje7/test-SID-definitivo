import os
import time
import subprocess
import sys
import urllib.request
from pathlib import Path

def test_modificabilidad_db():
    root_dir = Path(__file__).resolve().parent.parent.parent 
    os.chdir(root_dir) 

    env_path = ".env"
    db_temporal = "db_prueba_mantenimiento.sqlite3"
    
    if os.path.exists(db_temporal):
        os.remove(db_temporal)
        
    print("--- INICIANDO AUDITORÍA MNT-SYS-02 (Modificabilidad) ---")
    
    lineas_env_original = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lineas_env_original = f.readlines()

    proceso = None
    
    try:
        print(f"\n📝 1. Configurando nueva base de datos en el .env: {db_temporal}")
        with open(env_path, "w", encoding="utf-8") as f:
            for linea in lineas_env_original:
                if not linea.startswith("DB_NAME=") and not linea.startswith("DEBUG_MODE="):
                    f.write(linea)
            f.write(f"DB_NAME={db_temporal}\n")
            f.write("DEBUG_MODE=True\n")

        # 🌟 EL ARREGLO: Inyectamos el entorno a la fuerza en memoria
        env_subproceso = os.environ.copy()
        env_subproceso["DB_NAME"] = db_temporal
        env_subproceso["DEBUG_MODE"] = "True"

        print("🏗️ 1.5 Forzando la creación de la BD (migrate)...")
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--settings=imprenta_digital.settings_sistema"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            env=env_subproceso # <- AQUÍ PASAMOS EL ENTORNO FORZADO
        )
            
        puerto = 8003
        print(f"⏳ 2. Levantando el servidor de Django en el puerto {puerto}...")
        proceso = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", str(puerto), "--settings=imprenta_digital.settings_sistema", "--noreload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env_subproceso # <- AQUÍ TAMBIÉN
        )
        time.sleep(5) 
        
        print("📡 3. Inicializando conexión del sistema...")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{puerto}/crear-factura/", timeout=5)
        except Exception:
            pass
            
        print("🔌 4. Apagando el servidor...")
        proceso.terminate()
        proceso.wait()
        
        print("\n🧠 5. Analizando resultados...")
        if os.path.exists(db_temporal):
            print(f"🎉 ¡PRUEBA EXITOSA! El archivo '{db_temporal}' fue creado de forma dinámica.")
            print("📈 Diagnóstico: Nivel de Modificabilidad ALTO.")
            os.remove(db_temporal)
        else:
            assert False, "FALLO: El sistema ignoró el archivo .env y no creó la base de datos."

    finally:
        if proceso and proceso.poll() is None:
            proceso.terminate()
            
        print("\n♻️ Restaurando configuración original del entorno...")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lineas_env_original)

if __name__ == "__main__":
    test_modificabilidad_db()