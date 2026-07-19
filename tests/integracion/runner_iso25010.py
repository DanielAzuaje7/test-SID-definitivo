import os
import json
import subprocess
import re
from datetime import datetime

# 1. Creamos la estructura base del reporte de "hoy"
datos_grafana = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "proyecto": "SID - Imprenta Digital"
    },
    "mantenibilidad": {
        "pylint_score": 0.0,
        "radon_complejidad_alta": 0,
        "archivos_con_print": 0
    }
}

def ejecutar_mantenibilidad():
    print("==================================================")
    print("  INICIANDO SUITE DE MANTENIBILIDAD (ISO 25010)   ")
    print("==================================================")

    # --- MAN-01 y MAN-03: Pylint ---
    print("\n--- EJECUTANDO MAN-01 (Legibilidad) y MAN-03 (Modularidad) ---")
    try:
        resultado_pylint = subprocess.run(
            ["pylint", "Backend/"], 
            capture_output=True, text=True
        )
        match = re.search(r"Your code has been rated at ([\d\.]+)/10", resultado_pylint.stdout)
        if match:
            nota = float(match.group(1))
            datos_grafana["mantenibilidad"]["pylint_score"] = nota
            print(f"✅ Your code has been rated at {nota}/10")
        else:
            print("⚠️ No se pudo extraer la nota de Pylint.")
    except Exception as e:
        print(f"⚠️ Error ejecutando Pylint: {e}")

    # --- MAN-02: Complejidad Ciclomática (Radon) ---
    print("\n--- EJECUTANDO MAN-02 (Complejidad Ciclomática) ---")
    try:
        resultado_radon = subprocess.run(
            ["radon", "cc", "Backend/", "-s"], 
            capture_output=True, text=True
        )
        # Buscamos funciones con calificación C, D, E o F (alta complejidad)
        complejas = len(re.findall(r"\- [CDEF]", resultado_radon.stdout))
        datos_grafana["mantenibilidad"]["radon_complejidad_alta"] = complejas
        
        if complejas == 0:
            print("✅ Resultado: Aprobado. Todas las funciones tienen complejidad A o B.")
        else:
            print(f"❌ Resultado: Rechazado. Se encontraron {complejas} funciones complejas.")
    except Exception as e:
        print(f"⚠️ Error ejecutando Radon: {e}")

    # --- MAN-04: Facilidad de Diagnóstico (Prints) ---
    print("\n--- EJECUTANDO MAN-04 (Facilidad de Diagnóstico) ---")
    try:
        # Buscamos 'print(' en archivos .py dentro de Backend/
        resultado_grep = subprocess.run(
            ["grep", "-r", "print(", "Backend/", "--include=*.py"], 
            capture_output=True, text=True
        )
        archivos_print = len(set(resultado_grep.stdout.split('\n'))) - 1 if resultado_grep.stdout else 0
        datos_grafana["mantenibilidad"]["archivos_con_print"] = archivos_print

        if archivos_print == 0:
            print("✅ Resultado: Aprobado. No hay 'print()' perdidos.")
        else:
            print(f"❌ Resultado: Rechazado. Se encontraron 'print()' en {archivos_print} archivos.")
    except Exception as e:
        print(f"⚠️ Error buscando prints: {e}")

def consolidar_pytest():
    print("\n--- CONSOLIDANDO REPORTES DE PYTEST ---")
    
    reportes = {
        "reporte_unitarias.json": "pruebas_unitarias",
        "reporte_integracion.json": "pruebas_integracion",
        "reporte_sistemas.json": "pruebas_sistemas"
    }
    
    for archivo, llave in reportes.items():
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                
                # 1. Extraemos el resumen numérico (lo que ya tenías)
                datos_grafana[llave] = datos.get("summary", {})
                
                # 2. NUEVO: Extraemos el detalle de cada prueba
                lista_detalles = []
                for test in datos.get("tests", []):
                    lista_detalles.append({
                        "nombre": test.get("nodeid", "Desconocido").split("::")[-1], # Solo saca el nombre de la función
                        "estado": test.get("outcome", "unknown")
                    })
                
                # Guardamos la lista en una nueva llave (ej. "pruebas_sistemas_detalles")
                datos_grafana[f"{llave}_detalles"] = lista_detalles
                
            print(f"✅ {archivo} anexado al consolidado (Resumen + Detalles).")
        else:
            print(f"⚠️ No se encontró {archivo}. Se registrará con valores en cero.")
            datos_grafana[llave] = {"passed": 0, "failed": 0, "total": 0}
            datos_grafana[f"{llave}_detalles"] = []

def guardar_historial_grafana():
    archivo_historial = "historico_grafana.json"
    historial = []
    
    # 1. Si el historial ya existe, lo abrimos y lo leemos
    if os.path.exists(archivo_historial):
        with open(archivo_historial, "r", encoding="utf-8") as f:
            try:
                historial = json.load(f)
            except json.JSONDecodeError:
                pass # Si el archivo está corrupto o vacío, empezamos una lista nueva

    # 2. Agregamos la auditoría que acabamos de hacer al final de la lista
    historial.append(datos_grafana)
    
    # 3. Guardamos todo de vuelta en el archivo
    with open(archivo_historial, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)
        
    print("\n==================================================")
    print(f"  AUDITORÍA FINALIZADA - HISTORIAL ACTUALIZADO   ")
    print("==================================================")
    print(f"La corrida actual fue añadida a {archivo_historial}")

if __name__ == "__main__":
    ejecutar_mantenibilidad()
    consolidar_pytest()
    guardar_historial_grafana()