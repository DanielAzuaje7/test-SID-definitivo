import subprocess
import re

# Códigos de color para la consola
VERDE = '\033[92m'
ROJO = '\033[91m'
AMARILLO = '\033[93m'
RESET = '\033[0m'

def validar_mantenibilidad():
    print(f"{AMARILLO}=================================================={RESET}")
    print(f"{AMARILLO}  ANÁLISIS ESTÁTICO DE CÓDIGO (ISO 25010)  {RESET}")
    print(f"{AMARILLO}=================================================={RESET}")

    # --- 1. Pylint (Estándares PEP 8) ---
    print(f"\n{AMARILLO}--- Evaluando Pylint (Legibilidad) ---{RESET}")
    try:
        # Ejecutamos pylint y capturamos la salida
        resultado_pylint = subprocess.run(["pylint", "Backend/"], capture_output=True, text=True)
        
        # Buscamos la calificación
        match = re.search(r"Your code has been rated at ([\d\.]+)/10", resultado_pylint.stdout)
        if match:
            nota = float(match.group(1))
            color = VERDE if nota >= 7.0 else ROJO
            print(f"{color}Calificación Pylint: {nota}/10{RESET}")
            
            # Opcional: Imprimir las advertencias si la nota es baja
            if nota < 7.0:
                print("\nDetalles principales de Pylint:")
                # Muestra las primeras 10 líneas de advertencias
                print('\n'.join(resultado_pylint.stdout.split('\n')[:10])) 
                print("...")
        else:
            print(f"{ROJO}No se pudo calcular la nota de Pylint.{RESET}")
    except Exception as e:
        print(f"{ROJO}Error ejecutando Pylint: {e}{RESET}")

    # --- 2. Radon (Complejidad Ciclomática) ---
    print(f"\n{AMARILLO}--- Evaluando Radon (Complejidad Ciclomática) ---{RESET}")
    try:
        # Ejecutamos radon mostrando detalle ('-s')
        resultado_radon = subprocess.run(["radon", "cc", "Backend/", "-s"], capture_output=True, text=True)
        
        # Buscamos funciones con calificación C, D, E o F
        complejas = re.findall(r"(.* \- [CDEF])", resultado_radon.stdout)
        
        if not complejas:
            print(f"{VERDE}¡Excelente! Ninguna función superó la complejidad aceptable (A o B).{RESET}")
        else:
            print(f"{ROJO}Se encontraron {len(complejas)} funciones demasiado complejas:{RESET}")
            for funcion in complejas:
                print(f"  {ROJO}{funcion.strip()}{RESET}")
    except Exception as e:
        print(f"{ROJO}Error ejecutando Radon: {e}{RESET}")

    # --- 3. Prints Olvidados ---
    print(f"\n{AMARILLO}--- Evaluando Prints Olvidados ---{RESET}")
    try:
        resultado_grep = subprocess.run(["grep", "-rn", "print(", "Backend/", "--include=*.py"], capture_output=True, text=True)
        
        if not resultado_grep.stdout.strip():
            print(f"{VERDE}Limpio. No hay 'print()' en el código fuente.{RESET}")
        else:
            prints_encontrados = resultado_grep.stdout.strip().split('\n')
            print(f"{ROJO}Se encontraron 'print()' en las siguientes ubicaciones:{RESET}")
            for p in prints_encontrados[:5]: # Muestra solo los primeros 5 para no llenar la pantalla
                print(f"  {ROJO}{p}{RESET}")
            if len(prints_encontrados) > 5:
                print(f"  {ROJO}... y {len(prints_encontrados) - 5} más.{RESET}")
    except Exception as e:
        print(f"{ROJO}Error buscando prints: {e}{RESET}")

    print(f"\n{AMARILLO}=================================================={RESET}\n")

if __name__ == "__main__":
    validar_mantenibilidad()