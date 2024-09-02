from src.schedulers.base_scheduler import Scheduler
from src.models.process import Process, ProcessState

class SPN(Scheduler):
    def run(self):
        while self.processes or self.ready_queue or self.current_process:
            self.check_process_arrivals()
            self.check_process_completion()
            self.schedule_next_process()
            self.update_waiting_times()
            self.current_time += 1

    def check_process_arrivals(self):
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            process = self.processes.pop(0)
            process.state = ProcessState.READY
            self.ready_queue.append(process)
        self.ready_queue.sort(key=lambda p: p.cpu_burst_duration * p.cpu_bursts)

    def check_process_completion(self):
        if self.current_process:
            self.current_process.remaining_cpu_time -= 1
            if self.current_process.remaining_cpu_time == 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.turnaround_time = self.current_time - self.current_process.arrival_time + 1
                self.current_process = None

    def schedule_next_process(self):
        if not self.current_process and self.ready_queue:
            self.current_process = self.ready_queue.pop(0)
            self.current_process.state = ProcessState.RUNNING

    def update_waiting_times(self):
        for process in self.ready_queue:
            process.waiting_time += 1