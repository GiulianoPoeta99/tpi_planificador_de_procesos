from interfaces import PlanificadorDeProcesos, ResultadoPlanificador
from executors.fcfs import EjecutorFCFS
from executors.pe import EjecutorPE
from executors.rr import EjecutorRR
from executors.spn import EjecutorSPN
from executors.srtn import EjecutorSRTN

def ejecutar_planificacion(planificador: PlanificadorDeProcesos) -> ResultadoPlanificador:
    ejecutor_procesos = None
    
    if planificador.politica == 'fcfs':
        print('== Ejecutando planificador de procesos (política FSFC) ==')
        ejecutor_procesos = EjecutorFCFS(planificador)
    elif planificador.politica == 'rr':
        print('== Ejecutando planificador de procesos (política RR) ==')
        ejecutor_procesos = EjecutorRR(planificador)
    elif planificador.politica == 'spn':
        print('== Ejecutando planificador de procesos (política SPN) ==')
        ejecutor_procesos = EjecutorSPN(planificador)
    elif planificador.politica == 'srtn':
        print('== Ejecutando planificador de procesos (política SRTN) ==')
        ejecutor_procesos = EjecutorSRTN(planificador)
    elif planificador.politica == 'pe':
        print('== Ejecutando planificador de procesos (política PE) ==')
        ejecutor_procesos = EjecutorPE(planificador)
    else:
        raise ValueError('Error en política seleccionada - Falta implementación')

    print(planificador)
    return ejecutor_procesos.ejecutar()