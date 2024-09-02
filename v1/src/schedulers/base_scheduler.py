from typing import List
from src.models.process import Process, ProcessState

class Scheduler:
    def __init__(self, processes: List[Process]):
        self.processes = processes
        self.current_time = 0
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.current_process: Process = None

    def run(self):
        raise NotImplementedError("El método run debe ser implementado en las subclases")

    def check_io_completion(self):
        completed_io = []
        for process in self.blocked_queue:
            process.remaining_io_time -= 1
            if process.remaining_io_time == 0:
                completed_io.append(process)
        
        for process in completed_io:
            self.blocked_queue.remove(process)
            process.state = ProcessState.READY
            self.ready_queue.append(process)

    def move_to_io(self, process):
        process.state = ProcessState.BLOCKED
        process.remaining_io_time = process.io_burst_duration
        self.blocked_queue.append(process)
        self.current_process = None