from dataclasses import dataclass
from . import Process

@dataclass
class RunningProcess(Process):
    tip_already_executed: bool
    pending_cpu_burst_in_execution: int
    pending_io_burst_in_execution: int
    service_time: int
    ready_wait_time: int