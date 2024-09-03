from dataclasses import dataclass
from typing import List, Literal
from . import RunningProcess

@dataclass
class FinishedProcess(RunningProcess):
    return_instant: int
    return_time: int
    normalized_return_time: float