from dataclasses import dataclass
from enums import Task

@dataclass
class SystemState:
    order: int
    task: Task
    process_id: int = None
    process_name: str = None