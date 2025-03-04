# Monitoreo Telcel - On-Box-Junos

| Datos de entrada        | Actividad              | Detalle de la actividad                                                         | Datos Salida                                                                                  |
|-------------------------|------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| IP orígen, IP destino   | Pruebas de conectividad | Pruebas de ping de 50 pruebas cada 5 minutos, sin calidad de servicio            | Si la prueba es exitosa, 100% de paquetes respondidos y tiempos promedio menores a 100 ms, no ejecutar ninguna acción. Si se tienen paquetes perdidos, y tiempos mayores a 100 ms, después de 3 eventos, enviar alarma a correlacionador. Incluir en alarma Equipo origen e IP destino. |
