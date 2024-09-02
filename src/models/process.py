from dataclasses import dataclass
from . import StateProcess

@dataclass
class Process:
    nombre: str
    tiempo_arribo: int
    rafagas_cpu: int
    duracion_rafaga_cpu: int
    duracion_rafaga_io: int
    prioridad: int
    estado: StateProcess = StateProcess.NEW
    tiempo_cpu_restante: int = 0
    tiempo_retorno: int = 0
    tiempo_espera: int = 0