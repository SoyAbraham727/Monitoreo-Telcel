# Monitoreo Telcel - On-Box-Junos

## Descripción

El sistema de **Monitoreo Telcel - On-Box-Junos** está diseñado para realizar pruebas de conectividad entre equipos de red utilizando **ping**. Este monitoreo ayuda a verificar la estabilidad y calidad de la red en tiempo real, ejecutando pruebas periódicas y generando alertas en caso de eventos críticos, como paquetes perdidos o tiempos de respuesta altos.

## Tabla de Actividades

A continuación, se detalla el flujo de actividades y su correspondiente procesamiento:

| **Datos de entrada**        | **Actividad**            | **Detalle de la actividad**                                                         | **Datos de salida**                                                                                  |
|-----------------------------|--------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| IP origen, IP destino       | Pruebas de conectividad  | Se realizan 50 pruebas de ping cada 5 minutos sin calidad de servicio               | Si la prueba es exitosa, 100% de los paquetes son respondidos y los tiempos promedio son menores a 100 ms. Si se detectan paquetes perdidos o tiempos mayores a 100 ms, después de 3 eventos, se envía una alarma al correlacionador con la información del equipo origen y IP destino. |
