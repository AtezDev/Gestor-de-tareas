import os

NOMBRE_ARCHIVO = "mis_tareas.txt"

def cargar_tareas():
    """Carga las tareas desde el archivo de texto."""
    tareas = []
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                # Formato en archivo: nombre|completada
                partes = linea.strip().split("|")
                if len(partes) == 2:
                    tareas.append({"nombre": partes[0], "completada": partes[1] == "True"})
    return tareas

def guardar_tareas(tareas):
    """Guarda la lista de tareas en el archivo."""
    with open(NOMBRE_ARCHIVO, "w", encoding="utf-8") as f:
        for t in tareas:
            f.write(f"{t['nombre']}|{t['completada']}\n")

def mostrar_menu():
    print("\n--- GESTOR DE TAREAS v1.0 ---")
    print("1. Ver tareas")
    print("2. Agregar tarea")
    print("3. Marcar tarea como completada")
    print("4. Eliminar tarea")
    print("5. Salir")
    return input("Selecciona una opción: ")

def listar_tareas(tareas):
    if not tareas:
        print("\n[!] No hay tareas en la lista.")
    else:
        print("\n--- LISTA DE TAREAS ---")
        for i, t in enumerate(tareas, 1):
            estado = "✔" if t["completada"] else "✘"
            print(f"{i}. [{estado}] {t['nombre']}")

def main():
    tareas = cargar_tareas()
    
    while True:
        opcion = mostrar_menu()
        
        if opcion == "1":
            listar_tareas(tareas)
        
        elif opcion == "2":
            nombre = input("Nombre de la nueva tarea: ")
            if nombre:
                tareas.append({"nombre": nombre, "completada": False})
                guardar_tareas(tareas)
                print("Tarea agregada con éxito.")
        
        elif opcion == "3":
            listar_tareas(tareas)
            try:
                num = int(input("Número de tarea a completar: "))
                tareas[num-1]["completada"] = True
                guardar_tareas(tareas)
                print("¡Tarea actualizada!")
            except (ValueError, IndexError):
                print("[Error] Número inválido.")
        
        elif opcion == "4":
            listar_tareas(tareas)
            try:
                num = int(input("Número de tarea a eliminar: "))
                tarea_eliminada = tareas.pop(num-1)
                guardar_tareas(tareas)
                print(f"Eliminada: {tarea_eliminada['nombre']}")
            except (ValueError, IndexError):
                print("[Error] No se pudo eliminar.")
        
        elif opcion == "5":
            print("¡Hasta luego, analista!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()

    #  MADE BY ATEZ_DEV - 2026
