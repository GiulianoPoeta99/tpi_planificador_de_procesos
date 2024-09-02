from ..models import Process
from typing import List

class BaseScheduler:
    def __init__(self, procesos: List[Process]):
        self.procesos = procesos
        self.tiempo_actual = 0
        self.cola_listos: List[Process] = []
        self.proceso_actual: Process = None

    def ejecutar(self):
        raise NotImplementedError("Método ejecutar debe ser implementado en las subclases")