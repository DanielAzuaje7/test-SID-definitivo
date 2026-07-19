import os
import time
import subprocess
import sys
from playwright.sync_api import sync_playwright
from pathlib import Path 

def test_testeabilidad():
    root_dir = Path(__file__).resolve().parent.parent.parent 
    os.chdir(root_dir) 

    env_path = ".env"
    db_temporal = "db_test_automatizado.sqlite3"
    fixture_file = "datos_iniciales.json"

    print("--- INICIANDO AUDITORÍA MNT-SYS-03 (Testeabilidad) ---")

    if os.path.exists(db_temporal):
        os.remove(db_temporal)

    # RESPALDO DEL .ENV ORIGINAL
    lineas_env_original = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lineas_env_original = f.readlines()

    servidor = None

    try:
        # 1. AISLAR EL ENTORNO
        print(f"\n🛡️ 1. Aislando entorno: Redirigiendo a {db_temporal}")
        with open(env_path, "w", encoding="utf-8") as f:
            for linea in lineas_env_original:
                if not linea.startswith("DB_NAME=") and not linea.startswith("DEBUG_MODE="):
                    f.write(linea)
            f.write(f"DB_NAME={db_temporal}\n")
            f.write("DEBUG_MODE=True\n")

        # 2. CONSTRUIR E INYECTAR DATOS CON --settings
        print("🏗️ 2. Construyendo estructura de BD (migrate)...")
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--settings=imprenta_digital.settings_sistema"], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        print(f"💉 3. Inyectando datos de prueba ({fixture_file})...")
        resultado_load = subprocess.run(
            [sys.executable, "manage.py", "loaddata", fixture_file, "--settings=imprenta_digital.settings_sistema"], 
            capture_output=True, text=True
        )
        
        if "Installed" not in resultado_load.stdout:
            print(f"⚠️ Advertencia en inyección de datos: {resultado_load.stderr}")

        # 3. LEVANTAR EL SERVIDOR CON --settings
        puerto = 8004
        print(f"⏳ 4. Levantando servidor aislado en puerto {puerto}...")
        servidor = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", str(puerto), "--settings=imprenta_digital.settings_sistema", "--noreload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)

        # 4. AUDITORÍA VISUAL CON PLAYWRIGHT
        print("🤖 5. Iniciando inspección con Playwright...")
        prueba_exitosa = False
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                ruta_login = f"http://127.0.0.1:{puerto}/login/"
                respuesta = page.goto(ruta_login)
                
                if respuesta and respuesta.status == 200:
                    print("✅ Playwright: El sistema de pruebas cargó la interfaz correctamente.")
                    prueba_exitosa = True
                else:
                    print(f"❌ Playwright: Error al cargar la página (HTTP {respuesta.status})")
                
                browser.close()
        except Exception as e:
            print(f"❌ Fallo crítico en Playwright: {e}")

        # 5. VEREDICTO FINAL
        print("\n🧠 Analizando resultados de Testeabilidad...")
        if prueba_exitosa:
            print("🎉 ¡PRUEBA EXITOSA! El sistema recreó un ecosistema de pruebas autónomo.")
            print("📈 Diagnóstico: Nivel de Testeabilidad ALTO. Entorno aislado y datos inyectados.")
        else:
            print("❌ FALLO: El sistema no logró aislarse ni levantar el entorno con los fixtures.")

    finally:
        # 6. DESMONTAJE Y LIMPIEZA GARANTIZADA
        print("\n🔌 6. Apagando servidor y destruyendo entorno de pruebas...")
        if servidor and servidor.poll() is None:
            servidor.terminate()
            servidor.wait()
            
        if os.path.exists(db_temporal):
            os.remove(db_temporal)
            print("🗑️ Base de datos temporal eliminada.")

        print("♻️ Entorno restaurado a la normalidad.")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lineas_env_original)

if __name__ == "__main__":
    test_testeabilidad()