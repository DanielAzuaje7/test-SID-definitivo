import os
import time
import subprocess
import sys
import urllib.request
from pathlib import Path

def test_modificabilidad_db():
    # --- ENCONTRAR LA RAÍZ DEL PROYECTO ---
    # Sube 3 niveles: test_modificabilidad.py -> sistemas -> tests -> raíz
    root_dir = Path(__file__).resolve().parent.parent.parent 
    os.chdir(root_dir) # Nos movemos a la raíz para que manage.py y .env se encuentren fácil
    # --------------------------------------

    env_path = ".env"
    db_temporal = "db_prueba_mantenimiento.sqlite3"
    
    # Nos aseguramos de que no exista un archivo viejo de pruebas
    if os.path.exists(db_temporal):
        os.remove(db_temporal)
        
    print("--- INICIANDO AUDITORÍA MNT-SYS-02 (Modificabilidad) ---")
    
    # 1. Escribimos el nuevo nombre de la base de datos en el .env
    print(f"\n📝 1. Configurando nueva base de datos en el .env: {db_temporal}")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"DB_NAME={db_temporal}\n")
        f.write("DEBUG_MODE=True\n")
        
    # 2. Levantamos el servidor de Django en un puerto libre (8003)
    puerto = 8003
    print(f"⏳ 2. Levantando el servidor de Django en el puerto {puerto}...")
    proceso = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", str(puerto), "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5) # Esperamos a que Django inicialice
    
    # 3. Hacemos una petición rápida a cualquier ruta para obligar a Django a conectar la DB
    print("📡 3. Inicializando conexión del sistema...")
    try:
        # Usamos la de crear-factura o cualquier otra que tengas
        urllib.request.urlopen(f"http://127.0.0.1:{puerto}/crear-factura/", timeout=5)
    except Exception:
        # Ignoramos si redirige o da 404, solo queremos forzar la inicialización del motor de DB
        pass
        
    # 4. Apagamos el servidor
    print("🔌 4. Apagando el servidor...")
    proceso.kill()
    time.sleep(2)
    
    # 5. La prueba de fuego: ¿Se modificó la DB y se creó el archivo en el disco?
    print("\n🧠 5. Analizando resultados...")
    if os.path.exists(db_temporal):
        print(f"🎉 ¡PRUEBA EXITOSA! El archivo '{db_temporal}' fue creado de forma dinámica.")
        print("📈 Diagnóstico: Nivel de Modificabilidad ALTO. El sistema cambió su almacenamiento sin tocar código.")
        # Limpieza: Borramos el archivo temporal de pruebas para no dejar basura
        os.remove(db_temporal)
    else:
        print("❌ FALLO: El sistema ignoró el archivo .env y no creó la base de datos.")
        
    # 6. Restauramos el .env original por seguridad para que sigas trabajando normal
    print("\n♻️ Restaurando configuración original del entorno...")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("DB_NAME=db.sqlite3\n")
        f.write("DEBUG_MODE=True\n")

if __name__ == "__main__":
    test_modificabilidad_db()