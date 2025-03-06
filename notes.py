import os
import yaml
import jcs
from pathlib import Path

# Obtener la ruta del archivo YAML en el mismo directorio que el script
YAML_FILE = Path(__file__).parent / "destinos_telcel.yml"

def cargar_yaml():
    """Carga el archivo YAML y devuelve su contenido como un diccionario."""
    try:
        if not YAML_FILE.exists():
            jcs.syslog(CRITICAL_SEVERITY, f"El archivo YAML no existe: {YAML_FILE}")
            return {}

        with YAML_FILE.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except yaml.YAMLError as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error al leer el YAML: {e}")
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error inesperado al leer el YAML: {e}")
    
    return {}

