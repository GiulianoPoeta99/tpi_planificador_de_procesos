# tpi_planificador_de_procesos

Este es un simulador de cómo funcionan las políticas de planificación de procesos por parte de un procesador. Al ser un simulador, no funciona exactamente igual que un sistema operativo real.

## Dependencias

- Docker
- Docker compose

## Uso

1. Levantamos el contenedor con el siguiente comando en la terminal:

```bash
docker compose up -d
```

2. Ejecutamos el programa:

```bash
docker compose exec -it app python src/main.py
```

3. En la carpeta `./logs/YYYYMMDD_hhmmss_nombre_politica` se encuentran los resultados de la simulación:

    1. `parameters.log`: parámetros utilizados.
    2. `processes.log`: detalle de toda la ejecución.
    3. `summary.log`: resumen numérico de la simulación.
    4. `simulation_summary.svg`: imagen con métricas, diagrama de Gantt y resultados por proceso. Se puede abrir directamente con cualquier navegador.

4. Detener el contenedor

```bash
docker compose down
```
