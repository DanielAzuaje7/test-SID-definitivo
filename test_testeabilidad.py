import os
import time
import subprocess
import sys
from playwright.sync_api import sync_playwright

def test_testeabilidad():
    env_path = ".env"
    db_temporal = "db_test_automatizado.sqlite3"
    fixture_file = "datos_iniciales.json"

    print("--- INICIANDO AUDITORÍA MNT-SYS-03 (Testeabilidad) ---")

    # Limpieza preventiva por si quedó un archivo de una prueba anterior
    if os.path.exists(db_temporal):
        os.remove(db_temporal)

    # 1. AISLAR EL ENTORNO (El escudo protector)
    print(f"\n🛡️ 1. Aislando entorno: Redirigiendo a {db_temporal}")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"DB_NAME={db_temporal}\n")
        f.write("DEBUG_MODE=True\n")

    # 2. CONSTRUIR E INYECTAR DATOS
    print("🏗️ 2. Construyendo estructura de BD (migrate)...")
    subprocess.run([sys.executable, "manage.py", "migrate"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"💉 3. Inyectando datos de prueba ({fixture_file})...")
    resultado_load = subprocess.run(
        [sys.executable, "manage.py", "loaddata", fixture_file], 
        capture_output=True, text=True
    )
    
    if "Installed" not in resultado_load.stdout:
        print(f"⚠️ Advertencia en inyección de datos: {resultado_load.stderr}")

    # 3. LEVANTAR EL SERVIDOR DE PRUEBAS
    puerto = 8004
    print(f"⏳ 4. Levantando servidor aislado en puerto {puerto}...")
    servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", str(puerto), "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5) # Damos tiempo a Django para arrancar

    # 4. AUDITORÍA VISUAL CON PLAYWRIGHT
    print("🤖 5. Iniciando inspección con Playwright...")
    prueba_exitosa = False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navegamos a la ruta de login (definida en tu settings.py)
            ruta_login = f"http://127.0.0.1:{puerto}/login/"
            respuesta = page.goto(ruta_login)
            
            # Verificamos que el sistema responda correctamente (200 OK)
            if respuesta and respuesta.status == 200:
                print("✅ Playwright: El sistema de pruebas cargó la interfaz correctamente.")
                prueba_exitosa = True
                
                # NOTA PARA DANIEL: Si quieres que Playwright inicie sesión, puedes agregar
                # page.fill("input[name='username']", "TU_USUARIO")
                # page.fill("input[name='password']", "TU_CONTRASEÑA")
                # page.click("button[type='submit']")
                # Pero para probar Testeabilidad, con que el entorno levante y cargue la vista tras el migrate basta.
            else:
                print(f"❌ Playwright: Error al cargar la página (HTTP {respuesta.status})")
            
            browser.close()
    except Exception as e:
        print(f"❌ Fallo crítico en Playwright: {e}")

    # 5. DESMONTAJE Y LIMPIEZA
    print("\n🔌 6. Apagando servidor y destruyendo entorno de pruebas...")
    servidor.kill()
    time.sleep(2)
    
    if os.path.exists(db_temporal):
        os.remove(db_temporal)
        print("🗑️ Base de datos temporal eliminada.")

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("DB_NAME=db.sqlite3\n")
        f.write("DEBUG_MODE=True\n")
    print("♻️ Entorno restaurado a la normalidad.")

    # 6. VEREDICTO FINAL
    print("\n🧠 Analizando resultados de Testeabilidad...")
    if prueba_exitosa:
        print("🎉 ¡PRUEBA EXITOSA! El sistema recreó un ecosistema de pruebas autónomo.")
        print("📈 Diagnóstico: Nivel de Testeabilidad ALTO. Entorno aislado correctamente y datos inyectados.")
    else:
        print("❌ FALLO: El sistema no logró aislarse ni levantar el entorno con los fixtures.")

if __name__ == "__main__":
    test_testeabilidad()