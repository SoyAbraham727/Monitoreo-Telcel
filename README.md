# Monitoreo Telcel - On-Box-Junos

## Descripción

El sistema de **Monitoreo Telcel - On-Box-Junos** está diseñado para realizar pruebas de conectividad entre equipos de red utilizando **ping**. Este monitoreo ayuda a verificar la estabilidad y calidad de la red en tiempo real, ejecutando pruebas periódicas y generando alertas en caso de eventos críticos, como paquetes perdidos o tiempos de respuesta altos.

## Tabla de Actividades

A continuación, se detalla el flujo de actividades y su correspondiente procesamiento:

| **Datos de entrada**        | **Actividad**            | **Detalle de la actividad**                                                         | **Datos de salida**                                                                                  |
|-----------------------------|--------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| IP origen, IP destino       | Pruebas de conectividad  | Se realizan 50 pruebas de ping cada 5 minutos sin calidad de servicio               | Si la prueba es exitosa, 100% de los paquetes son respondidos y los tiempos promedio son menores a 100 ms. Si se detectan paquetes perdidos o tiempos mayores a 100 ms, después de 3 eventos, se envía una alarma al correlacionador con la información del equipo origen y IP destino. |


### Criterios de Aceptación

1. **Monitoreo de Conectividad**: 
   - La actividad de monitoreo debe realizar pruebas de conectividad entre las direcciones IP origen y destino con un intervalo de 5 minutos.
   - Cada ciclo de prueba debe realizar 50 intentos de `ping`.
   - Si los paquetes respondidos son 100% y el tiempo de respuesta promedio es menor a 100 ms, no se deben tomar acciones.
   - Si se presentan paquetes perdidos o tiempos mayores a 100 ms, se debe enviar una alarma al correlacionador después de tres eventos de fallas consecutivas.
   - La alarma debe incluir la dirección del equipo origen y la IP destino.

2. **Alarma y Reportes**: 
   - El sistema debe generar un reporte detallado de las alarmas, incluyendo el nombre del equipo de origen, IP destino y el motivo del evento de conectividad fallido.
   - El reporte debe poder ser consultado y exportado en formatos compatibles (por ejemplo, CSV o PDF).

3. **Interfaz de Usuario**: 
   - La interfaz debe mostrar de manera clara las IPs origen y destino, junto con el estado de las pruebas realizadas.
   - Los usuarios deben poder visualizar los reportes de manera interactiva.
   - La aplicación debe estar diseñada para ser intuitiva y fácil de usar, con acceso rápido a los detalles de cada evento de monitoreo.

---
