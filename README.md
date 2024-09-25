# tpi_planificador_de_procesos

Este es un simulador de como funciona las politicas de planificacion de procesos por parte de un procesador. Al ser un simulador esto no funciona exactamente igual que en la vida real.

## Dependencias

- Docker
- Docker compose

## Uso

1. Levantamos el contenedor con el siguiente coando en la terminal

```bash
docker compose up -d
```

2. Ejecutamos el siguiente comando en la terminal para ejecutar el programa

```bash
docker compose exec -it app python src/main.py
```

3. En la carpeta `./logs/YYYYMMDD_hhmmss_nombre_politica` se encuentran los resultados de la simulación que son 3 archivos:
    1. Los parametros,
    2. Toda la ejecución de los procesos,
    3. Un resumen de todo lo que sucedio en la simulación.

4. Detener el contenedor

```bash
docker compose down
```