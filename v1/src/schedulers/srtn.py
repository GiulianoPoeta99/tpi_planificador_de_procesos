from src.schedulers.base_scheduler import Scheduler
from src.models.process import Process, ProcessState

class SRTN(Scheduler):
    def run(self):
        while self.processes or self.ready_queue or self.blocked_queue or self.current_process:
            self.check_process_arrivals()
            self.check_process_completion()
            self.check_io_completion()
            self.schedule_next_process()
            self.update_waiting_times()
            self.current_time += 1

    def check_process_arrivals(self):
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            process = self.processes.pop(0)
            process.state = ProcessState.READY
            self.ready_queue.append(process)
        self.ready_queue.sort(key=lambda p: p.remaining_cpu_time)

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
        if self.ready_queue:
            shortest_process = min(self.ready_queue, key=lambda p: p.remaining_cpu_time)
            if not self.current_process or shortest_process.remaining_cpu_time < self.current_process.remaining_cpu_time:
                if self.current_process:
                    self.ready_queue.append(self.current_process)
                    self.current_process.state = ProcessState.READY
                self.current_process = self.ready_queue.pop(self.ready_queue.index(shortest_process))
                self.current_process.state = ProcessState.RUNNING