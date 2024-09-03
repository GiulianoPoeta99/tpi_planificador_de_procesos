from dataclasses import dataclass
from typing import List
from . import Process
from enums import Policy

@dataclass
class ProcessScheduler:
    policy: Policy
    processes: List[Process]
    tip: int
    tfp: int
    tcp: int
    quantum: int

    def __str__(self) -> str:
        return f"""Parameters:
  Policy: {self.policy.value}
  Number of Processes: {len(self.processes)}
  TIP: {self.tip}
  TFP: {self.tfp}
  TCP: {self.tcp}
  Quantum: {self.quantum}"""