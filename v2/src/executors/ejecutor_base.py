from abc import ABC, abstractmethod
from interfaces import PlanificadorDeProcesos, ResultadoPlanificador

class EjecutorProcesosStrategy(ABC):
    def __init__(self, planificador: PlanificadorDeProcesos):
        self.planificador = planificador

    @abstractmethod
    def ejecutar(self) -> ResultadoPlanificador:
        pass