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
    
    # RESPALDO DEL .ENV ORIGINAL
    lineas_env_original = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lineas_env_original = f.readlines()

    proceso = None
    
    try:
        # 1. Escribimos el .env seguro (conservando variables originales, modificando solo las necesarias)
        print(f"\n📝 1. Configurando nueva base de datos en el .env: {db_temporal}")
        with open(env_path, "w", encoding="utf-8") as f:
            for linea in lineas_env_original:
                if not linea.startswith("DB_NAME=") and not linea.startswith("DEBUG_MODE="):
                    f.write(linea)
            f.write(f"DB_NAME={db_temporal}\n")
            f.write("DEBUG_MODE=True\n")
            
        # 2. Levantamos el servidor con --settings
        puerto = 8003
        print(f"⏳ 2. Levantando el servidor de Django en el puerto {puerto}...")
        proceso = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", str(puerto), "--settings=imprenta_digital.settings_sistema", "--noreload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5) 
        
        # 3. Petición rápida
        print("📡 3. Inicializando conexión del sistema...")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{puerto}/crear-factura/", timeout=5)
        except Exception:
            pass
            
        # 4. Apagamos el servidor
        print("🔌 4. Apagando el servidor...")
        proceso.terminate()
        proceso.wait()
        
        # 5. Análisis
        print("\n🧠 5. Analizando resultados...")
        if os.path.exists(db_temporal):
            print(f"🎉 ¡PRUEBA EXITOSA! El archivo '{db_temporal}' fue creado de forma dinámica.")
            print("📈 Diagnóstico: Nivel de Modificabilidad ALTO. El sistema cambió su almacenamiento sin tocar código.")
            os.remove(db_temporal)
        else:
            print("❌ FALLO: El sistema ignoró el archivo .env y no creó la base de datos.")

    finally:
        # 6. RESTAURACIÓN GARANTIZADA PASE LO QUE PASE
        if proceso and proceso.poll() is None:
            proceso.terminate()
            
        print("\n♻️ Restaurando configuración original del entorno...")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lineas_env_original)

if __name__ == "__main__":
    test_modificabilidad_db()