import time
import yaml
import jcs
from jnpr.junos import Device
from junos import Junos_Context

# Constantes Globales de Configuración
YAML_FILE = "destinos_telcel.yml"
COUNT = 50  # Número de intentos de ping
RTT_THRESHOLD = 100  # Umbral de RTT en milisegundos
MAX_EVENTOS = 3  # Número de eventos consecutivos antes de enviar alarma
SLEEP_TIME = 300  # Tiempo de espera en segundos entre ejecuciones
ALERT_TIMEOUT = 900  # Tiempo en segundos para activar la alarma (15 minutos)

# Variables de configuración del sistema de logs
CRITICAL_SEVERITY = "external.critical"
WARNING_SEVERITY = "external.warning"

# Claves del archivo YAML
KEY_DESTINOS = "destinos"  # Clave para los destinos dentro de cada host
KEY_EVENTOS = "eventos"    # Clave para el contador de eventos en cada host

# Variable global para el número máximo de paquetes perdidos
MAX_PAQUETES_PERDIDOS = 0  # Variable que guarda el máximo de paquetes perdidos detectado


def cargar_yaml():
    """Carga el archivo YAML y devuelve su contenido como un diccionario."""
    try:
        with open(YAML_FILE, "r") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error al leer el YAML: {e}")
        return None
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error inesperado al leer el YAML: {e}")
        return None

def guardar_yaml(data):
    """Guarda la información actualizada en el archivo YAML."""
    try:
        with open(YAML_FILE, "w") as file:
            yaml.safe_dump(data, file)
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error al escribir el YAML: {e}")

def enviar_alarma(hostname, ip):
    """Envía una alarma al correlacionador tras 3 eventos consecutivos de fallo."""
    mensaje = f"ALARMA: {hostname} con destino {ip} ha fallado durante 15 minutos seguidos"
    jcs.syslog(CRITICAL_SEVERITY, mensaje)

def hacer_ping(dev, hostname, ip, data):
    """Ejecuta ping en un dispositivo Juniper y maneja eventos consecutivos fallidos."""
    try:
        result = dev.rpc.ping(host=ip, count=str(COUNT))

        # Extraer datos del XML
        paquetes_enviados = int(result.findtext("probe-results-summary/probes-sent").strip())
        paquetes_recibidos = int(result.findtext("probe-results-summary/probes-received").strip())
        perdida = paquetes_enviados - paquetes_recibidos
        avg_rtt = float(result.findtext("probe-results-summary/rtt-average").strip())

        # Manejo de eventos fallidos consecutivos
        if perdida > MAX_PAQUETES_PERDIDOS or avg_rtt > RTT_THRESHOLD:
            data[hostname][KEY_EVENTOS] += 1
            jcs.syslog(WARNING_SEVERITY, f"Degradación en {hostname} -> {ip}: Perdidos={perdida}, RTT={avg_rtt}ms")

            # Si hay 3 eventos seguidos, enviar alarma y reiniciar
            if data[hostname][KEY_EVENTOS] >= MAX_EVENTOS:
                enviar_alarma(hostname, ip)
                data[hostname][KEY_EVENTOS] = 0  # Reiniciar contador tras la alarma
        else:
            data[hostname][KEY_EVENTOS] = 0  # Reiniciar si la prueba es exitosa

    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Fallo en ping a {hostname} -> {ip} - Error: {str(e)}")

def main():
    dev = Device()
    try:
        dev.open()

        while True:
            data = cargar_yaml()
            if not data:
                return

            for hostname, info in data.items():
                for ip in info.get(KEY_DESTINOS, []):
                    hacer_ping(dev, hostname, ip, data)

            guardar_yaml(data)  # Guardar cambios en YAML
            time.sleep(SLEEP_TIME)  # Esperar antes de la siguiente ejecución

    finally:
        dev.close()  # Asegura que la conexión se cierre cuando el ciclo termine o haya un error

if __name__ == "__main__":
    main()
