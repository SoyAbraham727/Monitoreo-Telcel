import yaml
import jcs
from jnpr.junos import Device
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constantes Globales de Configuración
YAML_FILE = "destinos_telcel.yml"
COUNT = 50  # Número de intentos de ping
RTT_THRESHOLD = 100  # Umbral de RTT en milisegundos
MAX_EVENTOS = 3  # Número de eventos consecutivos antes de enviar alarma
ALERT_TIMEOUT = 900  # Tiempo en segundos para activar la alarma (15 minutos)
MAX_WORKERS = 10  # Número máximo de trabajadores (threads) en el pool

# Variables de configuración del sistema de logs
LOG_SEVERITY = "external.critical"
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
    except (yaml.YAMLError, Exception) as e:
        jcs.syslog(LOG_SEVERITY, f"Error al leer el YAML: {e}")
        return None


def guardar_yaml(data):
    """Guarda la información actualizada en el archivo YAML."""
    try:
        with open(YAML_FILE, "w") as file:
            yaml.safe_dump(data, file, default_flow_style=False)
    except Exception as e:
        jcs.syslog(LOG_SEVERITY, f"Error al escribir el YAML: {e}")


def enviar_alarma(hostname, ip):
    """Envía una alarma al correlacionador tras 3 eventos consecutivos de fallo."""
    mensaje = f"ALARMA: {hostname} con destino {ip} ha fallado durante 15 minutos seguidos"
    jcs.syslog(LOG_SEVERITY, mensaje)


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
        jcs.syslog(LOG_SEVERITY, f"Fallo en ping a {hostname} -> {ip} - Error: {str(e)}")


def procesar_ip(dev, hostname, ip, data):
    """Procesa el ping para una IP específica, de forma paralela."""
    hacer_ping(dev, hostname, ip, data)


def main():
    dev = Device()
    try:
        dev.open()

        # Cargar el archivo YAML una sola vez
        data = cargar_yaml()
        if not data:
            return

        # Crear un ThreadPoolExecutor con el número máximo de workers
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Enviar tareas para cada IP a los workers del executor
            futures = []
            for hostname, info in data.items():
                for ip in info.get(KEY_DESTINOS, []):
                    futures.append(executor.submit(procesar_ip, dev, hostname, ip, data))

            # Esperar que todos los hilos terminen su ejecución
            for future in as_completed(futures):
                pass  # Esperar a que todas las tareas se completen

        # Guardar cambios en YAML una vez que todos los pings se han procesado
        guardar_yaml(data)

    finally:
        dev.close()  # Asegura que la conexión se cierre cuando el ciclo termine o haya un error


if __name__ == "__main__":
    main()
