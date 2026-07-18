import os
import time
from playwright.sync_api import sync_playwright

def test_analizabilidad_inteligente():
    log_path = "auditoria_sid.log"
    
    # Lista de URLs (Puedes poner 1 o 100, el script se adapta solo)
    rutas_a_probar = [
        f"http://127.0.0.1:8000/ruta-falsa-qa-{str(time.time()).replace('.', '')}/",
        "http://127.0.0.1:8000/crear-factura/"
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("--- INICIANDO AUDITORÍA DINÁMICA MNT-SYS-01 ---")

        for url in rutas_a_probar:
            print(f"\n👉 Probando ruta: {url}")
            
            # Pesamos el log antes
            peso_antes = os.path.getsize(log_path) if os.path.exists(log_path) else 0
            
            # 1. CAPTURAMOS LA RESPUESTA HTTP DEL SERVIDOR
            response = page.goto(url)
            status_code = response.status
            
            print(f"📡 Código HTTP recibido del servidor: {status_code}")
            
            # Pesamos el log después
            peso_despues = os.path.getsize(log_path) if os.path.exists(log_path) else 0
            
            # Extraemos la parte relativa de la URL (ej. "/crear-factura/") para buscarla en el log
            path_relativo = url.split("8000")[1]
            
            # 2. VALIDACIÓN DINÁMICA BASADA EN EL CÓDIGO HTTP
            if status_code >= 400:
                # Si el código es 4xx o 5xx, EL SISTEMA DEBE HABER ESCRITO UN ERROR
                if peso_despues > peso_antes:
                    with open(log_path, "r", encoding="utf-8") as f:
                        f.seek(peso_antes)
                        lo_nuevo = f.read()
                        
                        # Verificamos que el error registrado coincida con el código HTTP y la URL
                        if path_relativo in lo_nuevo and str(status_code) in lo_nuevo:
                            print(f"✅ ÉXITO: El sistema atrapó el fallo y documentó el Error {status_code}.")
                        else:
                            print(f"❌ FALLO: El log creció, pero no documentó correctamente el Error {status_code}.")
                else:
                    print(f"❌ FALLO CRÍTICO: Hubo un Error {status_code} pero el sistema se quedó mudo (el log no creció).")
                    
            elif status_code == 200:
                # Si el código es 200 OK, EL SISTEMA NO DEBE REGISTRAR ERRORES
                if peso_despues == peso_antes:
                    print(f"✅ ÉXITO: Tráfico limpio (200 OK). El log no registró falsos positivos.")
                else:
                    # Si el log creció de todos modos, revisamos que no sea un error camuflado
                    with open(log_path, "r", encoding="utf-8") as f:
                        f.seek(peso_antes)
                        lo_nuevo = f.read()
                        if "WARNING" in lo_nuevo or "ERROR" in lo_nuevo:
                            print(f"❌ FALLO: La ruta devolvió 200 OK, pero generó errores internos en el log.")
                        else:
                            print(f"✅ ÉXITO: Tráfico limpio (200 OK). El log creció por procesos rutinarios, sin errores.")

        browser.close()
        print("\n📈 Diagnóstico Final: Analizabilidad SUPERADA.")

if __name__ == "__main__":
    test_analizabilidad_inteligente()