from typing import List
from models import RunningProcess, FinishedProcess, SchedulerResult
from .policy_strategy import PolicyStrategy
from tools.logger import CustomLogger

class FCFS(PolicyStrategy):
    def __init__(self, scheduler, logger: CustomLogger):
        super().__init__(scheduler, logger)

    def update_ready_queue(self):
        for process in self.scheduler.processes:
            if process.arrival_time == self.time_unit:
                self.ready_queue.append(RunningProcess(
                    id=process.id,
                    name=process.name,
                    arrival_time=process.arrival_time,
                    cpu_burst_duration=process.cpu_burst_duration,
                    io_burst_duration=process.io_burst_duration,
                    priority=process.priority,
                    tip_already_executed=self.scheduler.tip == 0,
                    pending_cpu_burst_in_execution=process.cpu_burst_duration,
                    pending_io_burst_in_execution=process.io_burst_duration,
                    service_time=0,
                    ready_wait_time=0,
                    cpu_burst_count=process.cpu_burst_count - 1 if process.cpu_burst_count > 0 else 0,
                    io_burst_count=process.io_burst_count
                ))
                self.logger.log_process_state(self.time_unit, f"Process {process.id} arrived and added to Ready Queue")

    def execute_tcp(self, process: RunningProcess):
        self.system_executor.execute_tcp_tick(process, self.time_unit)
        self.result.os_cpu_time += 1
        self.advance_time_unit()
        self.logger.log_process_state(self.time_unit, f"Executing TCP for Process {process.id}")

    def execute_tip(self, process: RunningProcess):
        for _ in range(self.scheduler.tip):
            self.system_executor.execute_tip_tick(process, self.time_unit)
            self.result.os_cpu_time += 1
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.log_process_state(self.time_unit, f"Executing TIP for Process {process.id}")

    def execute_tfp(self, process: RunningProcess):
        for _ in range(self.scheduler.tfp):
            self.system_executor.execute_tfp_tick(process, self.time_unit)
            self.result.os_cpu_time += 1
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.log_process_state(self.time_unit, f"Executing TFP for Process {process.id}")

    def execute_process(self, process: RunningProcess):
        if process.pending_cpu_burst_in_execution > 0:
            self.system_executor.execute_cpu_tick(process, self.time_unit)
            process.service_time += 1
            for i in range(1, len(self.ready_queue)):
                self.ready_queue[i].ready_wait_time += 1
            self.last_executed_process_id = process.id
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.log_process_state(self.time_unit, f"Executing CPU burst for Process {process.id}")

        if process.pending_cpu_burst_in_execution == 0:
            if process.cpu_burst_count > 0:
                process.cpu_burst_count -= 1
                process.pending_cpu_burst_in_execution = process.cpu_burst_duration
                self.io_blocked_queue.append(process)
                self.ready_queue.pop(0)
                self.logger.log_process_state(self.time_unit, f"Process {process.id} moved to I/O Blocked Queue")
                self.execute_tcp(process)
            elif process.cpu_burst_count == 0:
                self.execute_tfp(process)
                self.finish_process(process)

    def finish_process(self, process: RunningProcess):
        self.result.finished_processes.append(FinishedProcess(
            **process.__dict__,
            return_instant=self.time_unit,
            return_time=self.time_unit - process.arrival_time,
            normalized_return_time=(self.time_unit - process.arrival_time) / process.service_time
        ))
        self.ready_queue.pop(0)
        self.logger.log_process_state(self.time_unit, f"Process {process.id} finished")

    def execute(self) -> SchedulerResult:
        while len(self.result.finished_processes) < len(self.scheduler.processes):
            if not self.ready_queue:
                self.system_executor.execute_idle_tick(self.time_unit)
                self.result.idle_cpu_time += 1
                self.advance_time_unit()
                self.update_io_blocked_queue()
                self.update_ready_queue()
                self.logger.log_process_state(self.time_unit, "CPU Idle")
            else:
                current_process = self.ready_queue[0]
                if self.last_executed_process_id != current_process.id and not current_process.tip_already_executed:
                    self.execute_tip(current_process)
                    current_process.tip_already_executed = True
                    self.last_executed_process_id = current_process.id
                else:
                    self.execute_process(current_process)

        self.result.finished_processes.sort(key=lambda x: x.id)
        self.result.batch_return_time = self.time_unit
        self.result.average_batch_return_time = sum(p.return_time for p in self.result.finished_processes) / len(self.result.finished_processes)
        self.result.state_history = self.system_executor.get_history()
        return self.result