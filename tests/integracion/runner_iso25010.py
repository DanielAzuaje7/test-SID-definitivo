import os
import subprocess
import ast

# Rutas principales del proyecto SID
DIRECTORIO_BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Backend')
DIRECTORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def ejecutar_comando(comando, cwd=None):
    """Ejecuta un comando en consola y retorna su salida."""
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, cwd=cwd)
        return resultado.stdout + resultado.stderr
    except Exception as e:
        return str(e)

def test_man_01_y_03_pylint():
    print("\n--- EJECUTANDO MAN-01 (Legibilidad) y MAN-03 (Modularidad) ---")
    print("Auditando estándar PEP 8 y dependencias circulares con Pylint...")
    
    # Ejecutamos pylint sobre la carpeta Backend
    salida = ejecutar_comando(f"pylint {DIRECTORIO_BACKEND} --disable=all --enable=C0111,C0103,R0401")
    
    if "Your code has been rated at" in salida:
        # Pylint da un puntaje al final, extraemos ese texto
        linea_puntaje = [linea for linea in salida.split('\n') if "Your code has been rated at" in linea][0]
        print(f"Resultado: {linea_puntaje}")
        print("✅ MAN-01 / MAN-03 Completados. Revisa el puntaje arriba.")
    else:
        print("⚠️ Se encontraron problemas de formato o importaciones. Revisa la salida detallada:")
        print(salida[:500] + "...\n(Salida truncada)")

def test_man_02_complejidad():
    print("\n--- EJECUTANDO MAN-02 (Complejidad Ciclomática) ---")
    print("Analizando ramas y caminos lógicos con Radon...")
    
    # Radon cc analiza la complejidad, -nc filtra para mostrar solo grado C o peor (A y B son buenos)
    salida = ejecutar_comando(f"radon cc {DIRECTORIO_BACKEND} -nc")
    
    if not salida.strip():
        print("✅ Resultado: Aprobado. Todas las funciones tienen complejidad A o B.")
    else:
        print("❌ Resultado: Rechazado. Se encontraron funciones demasiado complejas (Grado C o peor):")
        print(salida)

def test_man_04_trazabilidad():
    print("\n--- EJECUTANDO MAN-04 (Facilidad de Diagnóstico) ---")
    print("Buscando uso de print() en lugar de logging estándar...")
    
    archivos_con_print = []
    
    # Buscamos en todos los archivos .py de Backend
    for raiz, _, archivos in os.walk(DIRECTORIO_BACKEND):
        for archivo in archivos:
            if archivo.endswith('.py'):
                ruta_completa = os.path.join(raiz, archivo)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    if 'print(' in contenido:
                        archivos_con_print.append(archivo)
                        
    if not archivos_con_print:
        print("✅ Resultado: Aprobado. No se detectaron 'print()' sueltos en el código.")
    else:
        print(f"❌ Resultado: Rechazado. Se encontraron 'print()' en: {', '.join(archivos_con_print)}")
        print("   Nota: Para cumplir la ISO 25010, se debe usar la librería 'logging'.")

def test_man_05_testeabilidad():
    print("\n--- EJECUTANDO MAN-05 (Testeabilidad / Cobertura) ---")
    print("Midiendo qué porcentaje del código cubren tus pruebas unitarias...")
    
    # Paso 1: Ejecutar las pruebas usando coverage
    comando_run = "coverage run manage.py test tests.unitarias"
    ejecutar_comando(comando_run, cwd=DIRECTORIO_RAIZ)
    
    # Paso 2: Generar el reporte solo para la carpeta Backend
    comando_report = f"coverage report --include=Backend/*"
    salida = ejecutar_comando(comando_report, cwd=DIRECTORIO_RAIZ)
    
    print(salida)
    print("✅ MAN-05 Completado. Revisa la columna 'Cover' en la tabla superior.")

if __name__ == "__main__":
    print("==================================================")
    print("  INICIANDO SUITE DE MANTENIBILIDAD (ISO 25010)   ")
    print("==================================================")
    test_man_01_y_03_pylint()
    test_man_02_complejidad()
    test_man_04_trazabilidad()
    test_man_05_testeabilidad()
    print("\n==================================================")
    print("               AUDITORÍA FINALIZADA               ")
    print("==================================================")