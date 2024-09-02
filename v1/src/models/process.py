from dataclasses import dataclass
from .process_state import ProcessState

@dataclass
class Process:
    name: str
    arrival_time: int
    cpu_bursts: int
    cpu_burst_duration: int
    io_burst_duration: int
    priority: int
    state: ProcessState = ProcessState.NEW
    remaining_cpu_time: int = 0
    remaining_io_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0