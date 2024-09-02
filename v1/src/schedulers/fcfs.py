from src.schedulers.base_scheduler import Scheduler
from src.models.process import Process, ProcessState

class FCFS(Scheduler):
    def run(self):
        while self.processes or self.ready_queue or self.blocked_queue or self.current_process:
            self.check_process_arrivals()
            self.check_process_completion()
            self.check_io_completion()
            self.schedule_next_process()
            self.update_waiting_times()
            self.current_time += 1

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

    def schedule_next_process(self):
        if not self.current_process and self.ready_queue:
            self.current_process = self.ready_queue.pop(0)
            self.current_process.state = ProcessState.RUNNING
            self.current_process.remaining_cpu_time = self.current_process.cpu_burst_duration