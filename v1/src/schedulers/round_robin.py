from src.schedulers.base_scheduler import Scheduler
from src.models.process import Process, ProcessState

class RoundRobin(Scheduler):
    def __init__(self, processes, quantum):
        super().__init__(processes)
        self.quantum = quantum
        self.time_in_quantum = 0

    def run(self):
        while self.processes or self.ready_queue or self.blocked_queue or self.current_process:
            self.check_process_arrivals()
            self.check_process_completion()
            self.check_io_completion()
            self.check_quantum_expiration()
            self.schedule_next_process()
            self.update_waiting_times()
            self.current_time += 1
            if self.current_process:
                self.time_in_quantum += 1

    def check_process_completion(self):
        if self.current_process:
            self.current_process.remaining_cpu_time -= 1
            if self.current_process.remaining_cpu_time == 0:
                if self.current_process.cpu_bursts > 1:
                    self.current_process.cpu_bursts -= 1
                    self.move_to_io(self.current_process)
                else:
                    self.current_process.state = ProcessState.TERMINATED
                    self.current_process.turnaround_time = self.current_time - self.current_process.arrival_time + 1
                self.current_process = None
                self.time_in_quantum = 0

    def check_quantum_expiration(self):
        if self.current_process and self.time_in_quantum == self.quantum:
            self.ready_queue.append(self.current_process)
            self.current_process.state = ProcessState.READY
            self.current_process = None
            self.time_in_quantum = 0
