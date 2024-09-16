from dataclasses import dataclass
from typing import List
from . import SystemState, FinishedProcess

@dataclass
class SchedulerResult:
    state_history: List[SystemState]
    finished_processes: List[FinishedProcess]
    batch_return_time: int
    average_batch_return_time: float
    idle_cpu_time: int
    os_cpu_time: int

    def __str__(self) -> str:
        return f"""  * Número de Estados del Sistema: {len(self.state_history)}
  * Número de Procesos Finalizados: {len(self.finished_processes)}
  * Tiempo de Retorno del Lote: {self.batch_return_time}
  * Tiempo Promedio de Retorno del Lote: {self.average_batch_return_time:.2f}
  * Tiempo de CPU Inactivo: {self.idle_cpu_time}
  * Tiempo de CPU del SO: {self.os_cpu_time}"""