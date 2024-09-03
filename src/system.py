from typing import List
from models import RunningProcess, SystemState
from enums import Task

class System:
    def __init__(self):
        self.history: List[SystemState] = []

    def execute_cpu_tick(self, process: RunningProcess, time_unit: int):
        process.pending_cpu_burst_in_execution -= 1
        self._add_to_history(time_unit, Task.EXECUTING_CPU, process)

    def execute_io_tick(self, process: RunningProcess, time_unit: int):
        process.pending_io_burst_in_execution -= 1
        self._add_to_history(time_unit - 1, Task.WAITING_IO, process)

    def execute_tip_tick(self, process: RunningProcess, time_unit: int):
        self._add_to_history(time_unit, Task.EXECUTING_TIP, process)

    def execute_tcp_tick(self, process: RunningProcess, time_unit: int):
        self._add_to_history(time_unit, Task.EXECUTING_TCP, process)

    def execute_tfp_tick(self, process: RunningProcess, time_unit: int):
        self._add_to_history(time_unit, Task.EXECUTING_TFP, process)

    def execute_idle_tick(self, time_unit: int):
        self._add_to_history(time_unit, Task.WAITING_IDLE)

    def _add_to_history(self, time_unit: int, task: Task, process: RunningProcess = None):
        self.history.append(SystemState(
            order=time_unit,
            task=task,
            process_id=process.id if process else None,
            process_name=process.name if process else None
        ))

    def get_history(self) -> List[SystemState]:
        return self.history