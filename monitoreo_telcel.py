import time
import yaml
import jcs
from jnpr.junos import Device

# Constantes globales de configuración
YAML_FILE = "destinos_telcel.yml"
COUNT = 50  # Número de intentos de ping
RTT_THRESHOLD = 100  # Umbral de RTT en milisegundos
MAX_EVENTOS = 3  # Número de eventos consecutivos antes de enviar alarma
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
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error inesperado al leer el YAML: {e}")
    return {}


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


def obtener_hostname(dev):
    """Obtiene el hostname del dispositivo Juniper utilizando RPC."""
    try:
        software_info = dev.rpc.get_software_information()
        hostname = software_info.findtext(".//host-name")
        if hostname:
            return hostname
        else:
            jcs.syslog(CRITICAL_SEVERITY, "No se pudo obtener el hostname del dispositivo.")
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Error al obtener el hostname: {str(e)}")
    return None


def hacer_ping(dev, hostname, ip):
    """Ejecuta ping en un dispositivo Juniper y devuelve el estado del resultado."""
    try:
        result = dev.rpc.ping(host=ip, count=str(COUNT))

        # Extraer datos del XML
        paquetes_enviados = int(result.findtext("probe-results-summary/probes-sent").strip())
        paquetes_recibidos = int(result.findtext("probe-results-summary/probes-received").strip())
        perdida = paquetes_enviados - paquetes_recibidos
        avg_rtt = float(result.findtext("probe-results-summary/rtt-average").strip())

        # Verifica si hubo pérdida de paquetes o si el RTT excedió el umbral
        if perdida > MAX_PAQUETES_PERDIDOS or avg_rtt > RTT_THRESHOLD:
            jcs.syslog(WARNING_SEVERITY, f"Degradación en {hostname} -> {ip}: Perdidos={perdida}, RTT={avg_rtt}ms")
            return False  # Retorna False si el ping falla
        else:
            return True  # Retorna True si el ping es exitoso
    except Exception as e:
        jcs.syslog(CRITICAL_SEVERITY, f"Fallo en ping a {hostname} -> {ip} - Error: {str(e)}")
    return False


def main():
    """Función principal para ejecutar el proceso de pings y manejar eventos."""
    dev = Device()
    try:
        dev.open()

        # Obtener el hostname del dispositivo
        hostname = obtener_hostname(dev)
        if not hostname:
            return  # Si no se pudo obtener el hostname, terminar el proceso

        # Cargar el archivo YAML una sola vez
        data = cargar_yaml()
        if not data:
            return
        
        # Procesar solo las IPs de destino que coincidan con el hostname
        if hostname in data:
            destinos = data[hostname].get(KEY_DESTINOS, [])
            eventos_count = data[hostname].get(KEY_EVENTOS, 0)

            # Variable para controlar si hubo alguna IP fallida en esta corrida
            alguna_falla = False

            # Verificar todas las IPs de destino
            for ip in destinos:
                if not hacer_ping(dev, hostname, ip):  # Si alguna IP falla
                    alguna_falla = True

            # Si alguna IP falló, incrementar el contador de eventos
            if alguna_falla:
                eventos_count += 1
                # Si hay 3 eventos seguidos, enviar alarma y reiniciar el contador
                if eventos_count >= MAX_EVENTOS:
                    enviar_alarma(hostname, destinos[0])  # Usamos la primera IP para la alarma
                    eventos_count = 0  # Reiniciar contador tras la alarma
            else:
                eventos_count = 0  # Reiniciar si todas las IPs son exitosas

            # Guardar cambios en YAML
            data[hostname][KEY_EVENTOS] = eventos_count
            guardar_yaml(data)

    finally:
        # Asegura que la conexión se cierre cuando el ciclo termine o haya un error
        dev.close()


if __name__ == "__main__":
    main()
