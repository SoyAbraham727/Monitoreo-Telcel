import os

# Ruta del archivo YAML
YAML_FILE = "destinos_telcel.yml"

def verificar_permisos(archivo):
    """Verifica si el archivo tiene permisos de lectura y escritura."""
    if not os.path.exists(archivo):
        print(f"El archivo '{archivo}' no existe.")
        return

    permisos = []
    if os.access(archivo, os.R_OK):
        permisos.append("Lectura OK")
    else:
        permisos.append("Lectura NO")

    if os.access(archivo, os.W_OK):
        permisos.append("Escritura OK")
    else:
        permisos.append("Escritura NO")

    print(f"Permisos del archivo '{archivo}': {', '.join(permisos)}")

if __name__ == "__main__":
    verificar_permisos(YAML_FILE)
