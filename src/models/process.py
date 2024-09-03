from dataclasses import dataclass

@dataclass
class Process:
    id: int
    name: str
    arrival_time: int
    cpu_burst_count: int
    cpu_burst_duration: int
    io_burst_count: int
    io_burst_duration: int
    priority: int