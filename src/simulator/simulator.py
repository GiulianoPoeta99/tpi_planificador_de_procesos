from typing import List, Tuple
from ..models import Process
from ..schedulers import BaseScheduler, FCFS, ExternalPriority, RoundRobin

class Simulator:
    def __init__(self, archivo_entrada: str, politica: str, parametros: dict):
        self.archivo_entrada = archivo_entrada
        self.politica = politica
        self.parametros = parametros
        self.procesos: List[Process] = []
        self.eventos: List[Tuple[int, str, Process]] = []

    def cargar_procesos(self):
        # Implementar lectura del archivo y creación de procesos
        pass

    def simular(self):
        self.cargar_procesos()
        planificador = self.crear_planificador()
        planificador.ejecutar()

    def crear_planificador(self) -> BaseScheduler:
        if self.politica == "FCFS":
            return FCFS(self.procesos)
        elif self.politica == "PrioridadExterna":
            return ExternalPriority(self.procesos)
        elif self.politica == "RoundRobin":
            return RoundRobin(self.procesos, self.parametros.get("quantum", 1))
        # Agregar más políticas aquí
        else:
            raise ValueError(f"Política de planificación no reconocida: {self.politica}")

    def generar_reporte(self):
        # Implementar generación de reporte con métricas
        pass