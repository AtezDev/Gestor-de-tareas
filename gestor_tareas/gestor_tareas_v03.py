# ===========================================================================
#            GESTOR DE TAREAS BÚNKER - VERSIÓN 2.1                           
# ===========================================================================
# Autor: Atez
# Descripción: Gestor de tareas robusto en CLI con validación estricta,
#              manejo de excepciones y persistencia de datos plana.
#              NUEVO: Sistema de autenticación encriptada con Bcrypt
#              y aislamiento de bóvedas por usuario en cascada.
# ===========================================================================

import os
import time
import colorama # Requiere: pip install colorama
import bcrypt   # Requiere: pip install bcrypt
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

# Archivo maestro de credenciales (El registro de acceso al búnker)
ARCHIVO_USUARIOS = "bunker_usuarios.txt"

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
    operativo de la lista actual.
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
#               MÓDULO DE AUTENTICACIÓN Y CRIPTOGRAFÍA
# ============================================================

def cargar_usuarios():
    """
    Lee la base de datos de credenciales.
    Lógica: Retorna un diccionario donde la 'key' es el username 
    y el 'value' es el hash de la contraseña. Si el archivo no existe,
    retorna un diccionario vacío indicando que no hay usuarios registrados.
    """
    usuarios = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = linea.strip().split("|")
                    if len(partes) == 2:
                        usuarios[partes[0]] = partes[1]
        except Exception:
            print(f"{C_ERROR}⚠️ Advertencia: Error al leer la base de datos de usuarios.")
            time.sleep(2)
    return usuarios

def guardar_usuario(username, hashed_password):
    """
    Guarda un nuevo usuario en la base de datos maestra.
    Lógica: Se usa el modo "a" (append) para añadir la línea al final 
    del archivo sin sobrescribir los usuarios existentes.
    """
    try:
        with open(ARCHIVO_USUARIOS, "a", encoding="utf-8") as f:
            f.write(f"{username}|{hashed_password}\n")
    except Exception:
        print(f"{C_ERROR}❌ Error crítico: No se pudo registrar el usuario en el disco.")
        time.sleep(2)

def registrar_usuario():
    """
    Controlador de registro con validación de seguridad y hashing.
    Lógica: Aplica una 'sal' criptográfica (salt) a la contraseña ingresada
    antes de hashearla, previniendo ataques de fuerza bruta o diccionarios.
    """
    limpiar()
    print(C_BORDE + "╔" + "═"*44 + "╗")
    print(C_BORDE + "║" + C_TITULO + "          REGISTRO DE NUEVO AGENTE          " + C_BORDE + "║")
    print(C_BORDE + "╚" + "═"*44 + "╝")
    
    usuarios_db = cargar_usuarios()
    
    while True:
        username = input(f"\n{C_INPUT}Nuevo Usuario (0 para volver): {Style.RESET_ALL}").strip().lower()
        if username == "0": return
        
        # Guardia de integridad para nombres de usuario
        if len(username) < 3 or not username.isalnum():
            print(f"{C_ERROR}❌ El usuario debe tener al menos 3 caracteres y ser alfanumérico.")
            continue
            
        if username in usuarios_db:
            print(f"{C_ERROR}❌ El nombre de usuario '{username}' ya está en uso. Elige otro.")
            continue
            
        password = input(f"{C_INPUT}Contraseña Maestra: {Style.RESET_ALL}").strip()
        if len(password) < 4:
            print(f"{C_ERROR}❌ La contraseña es demasiado débil (mínimo 4 caracteres).")
            continue
            
        if confirmar_accion(f"¿Crear credenciales para '{username}'?"):
            # Encriptación nivel Búnker: Transforma el string a bytes, aplica sal y hashea.
            pwd_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
            
            guardar_usuario(username, hashed_pwd)
            print(f"\n{C_EXITO}✅ Agente '{username}' registrado. Credenciales encriptadas exitosamente.")
            time.sleep(2)
            break

def iniciar_sesion():
    """
    Controlador de acceso mediante validación criptográfica.
    Lógica: Compara la contraseña plana ingresada contra el hash almacenado.
    Si coincide, retorna el 'username' para mantener el estado de la sesión.
    Si falla o el usuario no existe, retorna None, bloqueando el acceso.
    """
    limpiar()
    print(C_BORDE + "╔" + "═"*44 + "╗")
    print(C_BORDE + "║" + C_TITULO + "             CONTROL DE ACCESO              " + C_BORDE + "║")
    print(C_BORDE + "╚" + "═"*44 + "╝")
    
    usuarios_db = cargar_usuarios()
    if not usuarios_db:
        print(f"\n{C_ERROR}⚠️ No hay usuarios registrados en el Búnker. Regístrese primero.")
        time.sleep(2)
        return None
        
    username = input(f"\n{C_INPUT}Usuario: {Style.RESET_ALL}").strip().lower()
    if username not in usuarios_db:
        print(f"{C_ERROR}❌ Acceso denegado: Usuario no encontrado.")
        time.sleep(1.5)
        return None
        
    password = input(f"{C_INPUT}Contraseña: {Style.RESET_ALL}").strip()
    
    # Verificación Bcrypt: Compara el input plano contra el hash guardado
    hash_guardado = usuarios_db[username].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hash_guardado):
        print(f"\n{C_EXITO}🔓 Autenticación exitosa. Bienvenido, {username.capitalize()}.")
        time.sleep(1.5)
        return username
    else:
        print(f"\n{C_ERROR}❌ Acceso denegado: Contraseña incorrecta.")
        time.sleep(1.5)
        return None

# ============================================================
#               BÓVEDA DE DATOS DE TAREAS (PERSISTENCIA I/O)
# ============================================================

def obtener_archivo_usuario(username):
    """
    Genera un nombre de archivo dinámico y único.
    Lógica: Aísla los datos asegurando que un usuario no pueda 
    leer ni mutar las tareas de otro colega en el sistema.
    """
    return f"boveda_{username}.txt"

def cargar_tareas(username):
    """
    Lee el archivo local del usuario activo e inyecta los datos en memoria.
    Lógica: Se usa encoding='utf-8' para soportar tildes y caracteres especiales.
    Se emplea split('|') para separar la estructura 'NombreTarea|EstadoBooleano'.
    """
    archivo = obtener_archivo_usuario(username)
    tareas = []
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
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

def guardar_tareas(username, tareas):
    """
    Sobrescribe el archivo de texto del usuario con el estado actual de la memoria.
    Lógica: Se invoca después de CADA mutación de datos (Agregar, Eliminar, Completar)
    para asegurar que el estado persista incluso si hay un corte de energía inesperado.
    """
    archivo = obtener_archivo_usuario(username)
    try:
        with open(archivo, "w", encoding="utf-8") as f:
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

def agregar_tarea(username, tareas):
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
                # Se añade el diccionario a la lista y se sincroniza con el disco del usuario
                tareas.append({"nombre": nombre, "completada": False})
                guardar_tareas(username, tareas)
                print(f"\n{C_EXITO}✅ Tarea encapsulada y guardada con éxito. 🚀")
                time.sleep(1.5)
                break
            else:
                print(f"\n{C_INFO}Registro cancelado.")
                time.sleep(1)
                break

def completar_tarea(username, tareas):
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
                guardar_tareas(username, tareas)
                print(f"\n{C_EXITO}✅ ¡Excelente trabajo! Tarea marcada como lista.")
                time.sleep(1.5)
                break

def eliminar_tarea(username, tareas):
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
            guardar_tareas(username, tareas)
            print(f"\n{C_EXITO}🗑️ Eliminada: {tarea_eliminada['nombre']}")
            time.sleep(1.5)
            break
        else:
            print(f"\n{C_INFO}Operación cancelada. La tarea está a salvo en el búnker.")
            time.sleep(1.5)
            break

# ============================================================
#               INTERFAZ DASHBOARD BÚNKER (SESIÓN INICIADA)
# ============================================================

def menu_principal(username):
    """
    Controlador de estado interno (Dashboard). Exclusivo para usuarios autenticados.
    Mantiene el ciclo de vida de la sesión activa hasta que el usuario decida salir.
    Calcula dinámicamente métricas (Total, Listas, Pendientes) iterando la lista.
    """
    # Carga inicial a memoria RAM exclusiva del usuario
    tareas = cargar_tareas(username)
    
    while True:
        limpiar()
        
        # Cálculos de métricas en tiempo real mediante comprensión de generador
        total = len(tareas)
        completadas = sum(1 for t in tareas if t["completada"])
        pendientes = total - completadas
        
        # Renderizado de la UI principal (Búnker)
        print(C_BORDE + "╔═══════════════════════════════════════════╗")
        print(C_BORDE + "║" + f" {C_TITULO}📝 BÓVEDA DE: {username.upper()}".ljust(51) + C_BORDE + "║")
        print(C_BORDE + "╠═══════════════════════════════════════════╣")
        print(C_BORDE + "║ " + f"{C_INFO}📊 ESTADO DE LA BÓVEDA:{C_BORDE}".ljust(48) + "           ║")
        print(C_BORDE + "║ " + f"{C_TEXTO}Totales: {total:02d} {C_BORDE}| {C_EXITO}Listas: {completadas:02d} {C_BORDE}| {C_ERROR}Pendientes: {pendientes:02d} {C_BORDE}║")
        print(C_BORDE + "╚═══════════════════════════════════════════╝")
        print(f"{C_INFO} 1.{C_TEXTO} Ver lista de tareas")
        print(f"{C_INFO} 2.{C_TEXTO} Agregar nueva tarea")
        print(f"{C_INFO} 3.{C_TEXTO} Completar tarea")
        print(f"{C_INFO} 4.{C_TEXTO} Eliminar tarea")
        print(f"{C_ERROR} 5.{C_TEXTO} Cerrar Sesión (Log Out)")
        
        # Captura de input base (sin castear a entero todavía para evitar crashes por letras)
        op = input(f"\n{C_INPUT} Ingrese una opción: {Style.RESET_ALL}").strip()
        
        # Árbol de decisiones (Routing)
        if op == "1":
            limpiar()
            listar_tareas(tareas)
            input(f"\n{C_BORDE}[ENTER para volver al dashboard]{Style.RESET_ALL}")
        elif op == "2":
            agregar_tarea(username, tareas)
        elif op == "3":
            completar_tarea(username, tareas)
        elif op == "4":
            eliminar_tarea(username, tareas)
        elif op == "5":
            if confirmar_accion("¿Cerrar sesión y asegurar tu bóveda?"):
                limpiar()
                print(f"\n{C_EXITO}🔒 Sesión de {username.capitalize()} cerrada de forma segura.\n")
                time.sleep(1.5)
                break
        else:
            print(f"{C_ERROR}❌ Comando no reconocido. Intente nuevamente.")
            time.sleep(1.5)

# ============================================================
#               PUNTO DE ENTRADA (EXTERIOR DEL BÚNKER)
# ============================================================

def menu_acceso():
    """
    Capa externa de la aplicación.
    Maneja el routing principal antes de permitir acceso a cualquier bóveda.
    Actúa como el primer muro defensivo del sistema.
    """
    while True:
        limpiar()
        print(C_BORDE + "╔═══════════════════════════════════════════╗")
        print(C_BORDE + "║" + C_TITULO + "         🔒 SISTEMA BÚNKER v2.1        " + C_BORDE + " ║")
        print(C_BORDE + "╚═══════════════════════════════════════════╝")
        print(f"{C_INFO} 1.{C_TEXTO} Iniciar Sesión")
        print(f"{C_INFO} 2.{C_TEXTO} Registrar Nuevo Agente")
        print(f"{C_ERROR} 3.{C_TEXTO} Apagar Sistema")
        
        op = input(f"\n{C_INPUT}Seleccione operación: {Style.RESET_ALL}").strip()
        
        if op == "1":
            # Intentar login. Si es exitoso, pasa la sesión al nivel interno.
            usuario_logueado = iniciar_sesion()
            if usuario_logueado:
                menu_principal(usuario_logueado) 
        elif op == "2":
            registrar_usuario()
        elif op == "3":
            print(f"\n{C_EXITO}⚡ Apagando sistemas... ¡Hasta luego! 👋\n")
            time.sleep(1.5)
            break
        else:
            print(f"{C_ERROR}❌ Comando no reconocido."); time.sleep(1.5)

if __name__ == "__main__":
    try:
        # Se invoca el motor principal de la aplicación (Capa Externa)
        menu_acceso()
    except KeyboardInterrupt:
        # Blindaje Final: Atrapa el atajo Ctrl+C (Interrupción de Teclado).
        # Evita que el usuario vea un error feo (Traceback) en la consola si 
        # decide matar el proceso forzosamente.
        print(f"\n\n{C_EXITO}🔒 Interrupción detectada. Asegurando el perímetro y saliendo de forma segura...")
        time.sleep(1)

# MADE BY ATEZ_DEV - 2026