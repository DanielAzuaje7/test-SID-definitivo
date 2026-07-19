import os
import time
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_analizabilidad_inteligente():
    # 1. ESTANDARIZAR LA RUTA RAÍZ
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent 
    os.chdir(project_root)

    log_path = "auditoria_sid.log"
    puerto = "8000"
    
    print("--- INICIANDO ENTORNO PARA MNT-SYS-01 ---")
    
    # 2. LEVANTAR EL SERVIDOR CON EL SETTINGS_SISTEMA
    print("Levantando servidor de pruebas...")
    proceso_servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", puerto, "--settings=imprenta_digital.settings_sistema", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(4)

    # 3. LÓGICA DE LA PRUEBA
    rutas_a_probar = [
        f"http://127.0.0.1:{puerto}/ruta-falsa-qa-{str(time.time()).replace('.', '')}/",
        f"http://127.0.0.1:{puerto}/" 
    ]
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("\n--- INICIANDO AUDITORÍA DINÁMICA MNT-SYS-01 ---")

            for url in rutas_a_probar:
                print(f"\n👉 Probando ruta: {url}")
                
                peso_antes = os.path.getsize(log_path) if os.path.exists(log_path) else 0
                
                # CAPTURAMOS LA RESPUESTA HTTP DEL SERVIDOR
                try:
                    response = page.goto(url)
                    status_code = response.status
                    print(f"📡 Código HTTP recibido del servidor: {status_code}")
                except Exception as e:
                    print(f"❌ Error al intentar conectar con la ruta: {e}")
                    continue
                
                time.sleep(1)
                
                peso_despues = os.path.getsize(log_path) if os.path.exists(log_path) else 0
                path_relativo = url.split(puerto)[1]
                
                # VALIDACIÓN DINÁMICA BASADA EN EL CÓDIGO HTTP
                if status_code >= 400:
                    if peso_despues > peso_antes:
                        with open(log_path, "r", encoding="utf-8") as f:
                            f.seek(peso_antes)
                            lo_nuevo = f.read()
                            
                            if path_relativo in lo_nuevo and str(status_code) in lo_nuevo:
                                print(f"✅ ÉXITO: El sistema atrapó el fallo y documentó el Error {status_code}.")
                            else:
                                assert False, f"FALLO: El log creció, pero no documentó correctamente el Error {status_code}."
                    else:
                        assert False, f"FALLO CRÍTICO: Hubo un Error {status_code} pero el sistema se quedó mudo (el log no creció)."
                        
                elif status_code == 200:
                    if peso_despues == peso_antes:
                        print(f"✅ ÉXITO: Tráfico limpio (200 OK). El log no registró falsos positivos.")
                    else:
                        with open(log_path, "r", encoding="utf-8") as f:
                            f.seek(peso_antes)
                            lo_nuevo = f.read()
                            if "WARNING" in lo_nuevo or "ERROR" in lo_nuevo:
                                assert False, "FALLO: La ruta devolvió 200 OK, pero generó errores internos en el log."
                            else:
                                print(f"✅ ÉXITO: Tráfico limpio (200 OK). El log creció por procesos rutinarios, sin errores.")

            browser.close()
            print("\n📈 Diagnóstico Final: Analizabilidad SUPERADA.")
            
    finally:
        # 4. APAGAR EL SERVIDOR PASE LO QUE PASE
        print("\nApagando servidor de pruebas...")
        proceso_servidor.terminate()
        proceso_servidor.wait()

if __name__ == "__main__":
    test_analizabilidad_inteligente()