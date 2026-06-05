# ===========================================================================
#            GESTOR DE TAREAS BÚNKER - VERSIÓN 2.0                           
# ===========================================================================
# Autor: Atez
# Descripción: Gestor de tareas robusto en CLI con validación estricta,
#              manejo de excepciones y persistencia de datos plana.
#              Diseñado con arquitectura de cascada para evitar bloqueos.
# ===========================================================================

import os
import time
import colorama
from colorama import Fore, Style

# Inicializar Colorama para habilitar secuencias ANSI en la consola de Windows
colorama.init(autoreset=True)

# --- CONFIGURACIÓN DE COLORES Y ESTILOS (CAPA DE PRESENTACIÓN) ---
# Se utilizan variables constantes para mantener consistencia en la UI
# y facilitar futuros cambios de temas sin reescribir todo el código.
C_BORDE   = Fore.LIGHTBLACK_EX + Style.BRIGHT  # Gris oscuro/Negro para el búnker
C_TITULO  = Fore.GREEN + Style.BRIGHT
C_INPUT   = Fore.MAGENTA + Style.BRIGHT
C_INFO    = Fore.CYAN + Style.BRIGHT
C_EXITO   = Fore.GREEN + Style.BRIGHT
C_ERROR   = Fore.RED + Style.BRIGHT
C_TEXTO   = Fore.WHITE + Style.BRIGHT

# Archivo de persistencia de datos
NOMBRE_ARCHIVO = "mis_tareas.txt"

# ============================================================
#               MÓDULOS DEL SISTEMA Y VALIDACIÓN
# ============================================================

def limpiar():
    """
    Limpia la consola independientemente del sistema operativo.
    'nt' es para Windows (usa cls), el resto (Linux/Mac) usa 'clear'.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def confirmar_accion(mensaje):
    """
    Guardia de confirmación booleana (Sí/No).
    Lógica: Atrapa al usuario en un bucle infinito (while True) hasta que 
    entregue una respuesta válida. Evita que un simple 'Enter' o tecla 
    equivocada ejecute acciones destructivas.
    """
    while True:
        res = input(f"\n{C_INPUT}{mensaje} (S/N): {Style.RESET_ALL}").strip().upper()
        if res in ['S', 'SI', 'Y']: return True
        if res in ['N', 'NO']: return False
        print(f"{C_ERROR}❌ Error: Comando no reconocido. Debe ingresar 'S' o 'N'.")

def ingresar_entero(mensaje, min_val, max_val):
    """
    Guardia numérico paramétrico.
    Lógica: Reemplaza múltiples bloques try-except. Valida que el input 
    sea puramente numérico (isdigit) y que se encuentre dentro del rango 
    operativo de la lista de tareas actual.
    Incluye '0' como escape de emergencia (Return to Menu).
    """
    while True:
        entrada = input(f"{C_INPUT}{mensaje}{Style.RESET_ALL}").strip()
        
        # El 0 actúa como un break lógico para abortar la operación actual
        if entrada == "0": 
            return 0  
        
        if entrada.isdigit():
            num = int(entrada)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"{C_ERROR}❌ Error: El número debe estar entre {min_val} y {max_val}.")
        else:
            print(f"{C_ERROR}❌ Error: Debe ingresar un valor numérico válido.")

# ============================================================
#               BÓVEDA DE DATOS (PERSISTENCIA I/O)
# ============================================================

def cargar_tareas():
    """
    Lee el archivo local e inyecta los datos en la memoria (Lista de diccionarios).
    Lógica: Se usa encoding='utf-8' para soportar tildes y caracteres especiales.
    Se emplea split('|') para separar la estructura 'NombreTarea|EstadoBooleano'.
    """
    tareas = []
    if os.path.exists(NOMBRE_ARCHIVO):
        try:
            with open(NOMBRE_ARCHIVO, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = linea.strip().split("|")
                    if len(partes) == 2:
                        # Reconstruye el diccionario evaluando si el string es "True"
                        tareas.append({"nombre": partes[0], "completada": partes[1] == "True"})
        except Exception:
            # Captura errores de lectura (ej. archivo corrupto o sin permisos)
            print(f"{C_ERROR}⚠️ Advertencia: No se pudo leer el archivo de tareas correctamente.")
            time.sleep(2)
    return tareas

def guardar_tareas(tareas):
    """
    Sobrescribe el archivo de texto local con el estado actual de la memoria.
    Lógica: Se invoca después de CADA mutación de datos (Agregar, Eliminar, Completar)
    para asegurar que el estado persista incluso si hay un corte de energía inesperado.
    """
    try:
        with open(NOMBRE_ARCHIVO, "w", encoding="utf-8") as f:
            for t in tareas:
                # Serialización básica: se concatenan los valores usando un pipe '|'
                f.write(f"{t['nombre']}|{t['completada']}\n")
    except Exception:
        print(f"{C_ERROR}❌ Error crítico: No se pudo guardar la información en el disco.")
        time.sleep(2)

# ============================================================
#               MÓDULOS DE OPERACIÓN LÓGICA (CRUD)
# ============================================================

def listar_tareas(tareas, mostrar_vacias=True):
    """
    Renderiza la lista de tareas formateada.
    Retorna False si la lista está vacía, lo cual actúa como señal
    para abortar operaciones dependientes (como eliminar o completar).
    """
    if not tareas:
        if mostrar_vacias:
            print(f"\n{C_INFO}📭 La bóveda de tareas está vacía. ¡Agrega una nueva!")
        return False

    print(C_BORDE + "\n" + "─"*12 + f" {C_INFO}TUS TAREAS{C_BORDE} " + "─"*12)
    for i, t in enumerate(tareas, 1):
        estado = f"{C_EXITO}✔ Completada" if t["completada"] else f"{C_ERROR}✘ Pendiente "
        # Format {i:02d} asegura que los números menores a 10 tengan un cero (ej. 01, 02)
        print(f"{C_BORDE}[{C_TEXTO}{i:02d}{C_BORDE}] {estado} {C_BORDE}| {C_INFO}{t['nombre']}")
    print(C_BORDE + "─"*36)
    return True

def agregar_tarea(tareas):
    """
    Módulo para inyectar nuevos registros (Create).
    Incluye validación de string para evitar strings vacíos o inyecciones
    del carácter reservado '|' que corrompería el método de guardado.
    """
    limpiar()
    print(C_BORDE + "╔" + "═"*44 + "╗")
    print(C_BORDE + "║" + C_TITULO + "          AGREGAR NUEVA TAREA         " + C_BORDE + "║")
    print(C_BORDE + "╚" + "═"*44 + "╝")
    
    while True:
        nombre = input(f"\n{C_INPUT}Descripción de la tarea (0 para volver): {Style.RESET_ALL}").strip()
        
        if nombre == "0":
            break
        elif len(nombre) < 3:
            print(f"{C_ERROR}❌ Error: El nombre de la tarea es muy corto (mínimo 3 caracteres).")
        elif "|" in nombre:
            # Prevención de corrupción de datos al leer el .txt
            print(f"{C_ERROR}❌ Error: El carácter '|' está reservado por el sistema.")
        else:
            if confirmar_accion(f"¿Guardar la tarea '{nombre}'?"):
                # Se añade el diccionario a la lista y se sincroniza con el disco
                tareas.append({"nombre": nombre, "completada": False})
                guardar_tareas(tareas)
                print(f"\n{C_EXITO}✅ Tarea encapsulada y guardada con éxito. 🚀")
                time.sleep(1.5)
                break
            else:
                print(f"\n{C_INFO}Registro cancelado.")
                time.sleep(1)
                break

def completar_tarea(tareas):
    """
    Módulo para actualizar el estado del registro (Update).
    Verifica primero si hay tareas; si no, retorna al menú.
    Valida si la tarea ya fue completada antes para evitar procesos redundantes.
    """
    while True:
        limpiar()
        # Si listar_tareas retorna False, cortamos la ejecución de la función
        if not listar_tareas(tareas):
            time.sleep(2)
            break
            
        print(f"\n{C_BORDE}(Ingresa {C_TEXTO}0{C_BORDE} para abortar la operación)")
        opcion = ingresar_entero("Selecciona el número de la tarea a completar: ", 1, len(tareas))
        
        if opcion == 0:
            break
            
        # Mapeo de índice humano (empieza en 1) a índice informático (empieza en 0)
        tarea = tareas[opcion-1]
        
        if tarea["completada"]:
            print(f"\n{C_INFO}ℹ️ La tarea '{tarea['nombre']}' ya estaba completada.")
            time.sleep(1.5)
        else:
            if confirmar_accion(f"¿Marcar '{tarea['nombre']}' como completada?"):
                tarea["completada"] = True
                guardar_tareas(tareas)
                print(f"\n{C_EXITO}✅ ¡Excelente trabajo! Tarea marcada como lista.")
                time.sleep(1.5)
                break

def eliminar_tarea(tareas):
    """
    Módulo para purgar registros de la memoria y el disco (Delete).
    Contiene la barrera psicológica más alta (doble confirmación) al ser
    una acción destructiva e irreversible.
    """
    while True:
        limpiar()
        if not listar_tareas(tareas):
            time.sleep(2)
            break
            
        print(f"\n{C_BORDE}(Ingresa {C_TEXTO}0{C_BORDE} para abortar la operación)")
        opcion = ingresar_entero("Selecciona el número de la tarea a ELIMINAR: ", 1, len(tareas))
        
        if opcion == 0:
            break
            
        tarea_actual = tareas[opcion-1]
        
        print(f"\n{C_ERROR}⚠️ ATENCIÓN: Esta acción es irreversible.")
        if confirmar_accion(f"¿Estás ABSOLUTAMENTE seguro de eliminar '{tarea_actual['nombre']}'?"):
            # pop() extrae y elimina el elemento en un solo movimiento
            tarea_eliminada = tareas.pop(opcion-1)
            guardar_tareas(tareas)
            print(f"\n{C_EXITO}🗑️ Eliminada: {tarea_eliminada['nombre']}")
            time.sleep(1.5)
            break
        else:
            print(f"\n{C_INFO}Operación cancelada. La tarea está a salvo en el búnker.")
            time.sleep(1.5)
            break

# ============================================================
#               INTERFAZ PRINCIPAL (MAIN LOOP)
# ============================================================

def menu_principal():
    """
    Controlador de estado (Dashboard).
    Mantiene el ciclo de vida de la aplicación activo hasta que el usuario decida salir.
    Calcula dinámicamente métricas (Total, Listas, Pendientes) iterando la lista de diccionarios.
    """
    # Carga inicial a memoria RAM
    tareas = cargar_tareas()
    
    while True:
        limpiar()
        
        # Cálculos de métricas en tiempo real mediante comprensión de generador
        total = len(tareas)
        completadas = sum(1 for t in tareas if t["completada"])
        pendientes = total - completadas
        
        # Renderizado de la UI principal (Búnker)
        print(C_BORDE + "╔═══════════════════════════════════════════╗")
        print(C_BORDE + "║" + C_TITULO + "         📝 GESTOR DE TAREAS v2.0      " + C_BORDE + "    ║")
        print(C_BORDE + "╠═══════════════════════════════════════════╣")
        print(C_BORDE + "║ " + f"{C_INFO}📊 ESTADO DE LA BÓVEDA:{C_BORDE}".ljust(48) + "           ║")
        print(C_BORDE + "║ " + f"{C_TEXTO}Totales: {total:02d} {C_BORDE}| {C_EXITO}Listas: {completadas:02d} {C_BORDE}| {C_ERROR}Pendientes: {pendientes:02d} {C_BORDE}║")
        print(C_BORDE + "╚═══════════════════════════════════════════╝")
        print(f"{C_INFO} 1.{C_TEXTO} Ver lista de tareas")
        print(f"{C_INFO} 2.{C_TEXTO} Agregar nueva tarea")
        print(f"{C_INFO} 3.{C_TEXTO} Completar tarea")
        print(f"{C_INFO} 4.{C_TEXTO} Eliminar tarea")
        print(f"{C_ERROR} 5.{C_TEXTO} Salir del sistema")
        
        # Captura de input base (sin castear a entero todavía para evitar crashes por letras)
        op = input(f"\n{C_INPUT} Ingrese una opción: {Style.RESET_ALL}").strip()
        
        # Árbol de decisiones (Routing)
        if op == "1":
            limpiar()
            listar_tareas(tareas)
            input(f"\n{C_BORDE}[ENTER para volver al dashboard]{Style.RESET_ALL}")
        elif op == "2":
            agregar_tarea(tareas)
        elif op == "3":
            completar_tarea(tareas)
        elif op == "4":
            eliminar_tarea(tareas)
        elif op == "5":
            if confirmar_accion("¿Cerrar y asegurar la bóveda de tareas?"):
                limpiar()
                print(f"\n{C_EXITO}🔒 Bóveda asegurada. ¡Hasta la próxima, Atez! 👋\n")
                time.sleep(1.5)
                break
        else:
            print(f"{C_ERROR}❌ Comando no reconocido. Intente nuevamente.")
            time.sleep(1.5)

# ============================================================
#               PUNTO DE ENTRADA AL SISTEMA
# ============================================================

if __name__ == "__main__":
    try:
        # Se invoca el motor principal de la aplicación
        menu_principal()
    except KeyboardInterrupt:
        # Blindaje Final: Atrapa el atajo Ctrl+C (Interrupción de Teclado).
        # Evita que el usuario vea un error feo (Traceback) en la consola si 
        # decide matar el proceso forzosamente.
        print(f"\n\n{C_EXITO}🔒 Interrupción detectada. Saliendo del sistema de forma segura...")
        time.sleep(1)

# MADE BY ATEZ_DEV - 2026