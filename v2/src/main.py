from scheduler import ejecutar_planificacion
from interfaces import PlanificadorDeProcesos, Proceso

def main():
    # Crear algunos procesos de ejemplo
    procesos = [
        Proceso(id=1, nombre="Proceso 1", tiempo_de_arribo=0, cantidad_de_rafagas_cpu=2, duracion_rafaga_cpu=3, cantidad_de_rafagas_io=1, duracion_rafaga_io=2, prioridad=1),
        Proceso(id=2, nombre="Proceso 2", tiempo_de_arribo=1, cantidad_de_rafagas_cpu=3, duracion_rafaga_cpu=2, cantidad_de_rafagas_io=2, duracion_rafaga_io=1, prioridad=2),
        # Añade más procesos según sea necesario
    ]

    # Configurar el planificador
    planificador = PlanificadorDeProcesos(
        politica='fcfs',
        procesos=procesos,
        tip=1,
        tfp=1,
        tcp=1,
        quantum=2
    )
    
    resultado = ejecutar_planificacion(planificador)
    print(resultado)

if __name__ == "__main__":
    main()