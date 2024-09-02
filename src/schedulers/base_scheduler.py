from typing import List
from src.models.process import Process

class Scheduler:
    def __init__(self, processes: List[Process]):
        self.processes = processes
        self.current_time = 0
        self.ready_queue: List[Process] = []
        self.current_process: Process = None

    def run(self):
        raise NotImplementedError("The run method must be implemented in subclasses")