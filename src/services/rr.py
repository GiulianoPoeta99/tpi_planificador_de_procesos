from typing import List
from models import RunningProcess, FinishedProcess, SchedulerResult
from system import System
from .policy_strategy import PolicyStrategy
from tools.logger import CustomLogger

class RoundRobin(PolicyStrategy):
    def __init__(self, scheduler, logger: CustomLogger):
        self.scheduler = scheduler
        self.logger = logger

        self.time_unit = 0
        self.ready_queue: List[RunningProcess] = []
        self.io_blocked_queue: List[RunningProcess] = []
        self.last_executed_process = None
        self.result = SchedulerResult(
            state_history=[],
            finished_processes=[],
            batch_return_time=0,
            average_batch_return_time=0,
            idle_cpu_time=0,
            os_cpu_time=0
        )
        self.system_executor = System()
        self.update_io_blocked_queue()
        self.update_ready_queue()
        self.quantum_counter = 0
        self.quantum_expired = False

    def advance_time_unit(self):
        self.logger.log_ws()
        self.time_unit += 1

    def update_io_blocked_queue(self):
        processes_reviewed = 0
        while processes_reviewed < len(self.io_blocked_queue):
            process = self.io_blocked_queue[processes_reviewed]
            if process.pending_io_burst_in_execution > 0:
                self.system_executor.execute_io_tick(process, self.time_unit)
                self.logger.info(self.time_unit, 'BLOCKED', f"Process '{process.name}' (pid: {process.id}) is executing I/O")

            if process.pending_io_burst_in_execution == 0:
                if process.io_burst_count > 0:
                    process.io_burst_count -= 1
                    process.pending_io_burst_in_execution = process.io_burst_duration

                process.recently_moved_to_ready_queue = True
                self.ready_queue.append(process)
                self.io_blocked_queue.pop(processes_reviewed)
                self.logger.info(self.time_unit, 'BLOCKED', f"Process '{process.name}' (pid: {process.id}) was moved from I/O to Ready Queue")
            else:
                processes_reviewed += 1

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
                    recently_moved_to_ready_queue=True,
                    pending_cpu_burst_in_execution=process.cpu_burst_duration,
                    pending_io_burst_in_execution=process.io_burst_duration,
                    service_time=0,
                    ready_wait_time=0,
                    cpu_burst_count=process.cpu_burst_count - 1 if process.cpu_burst_count > 0 else 0,
                    io_burst_count=process.io_burst_count
                ))
                self.logger.info(self.time_unit, 'READY', f"Process '{process.name}' (pid: {process.id}) has arrived and added to Ready Queue")

    def execute_tip(self, process: RunningProcess):
        for _ in range(self.scheduler.tip):
            self.system_executor.execute_tip_tick(process, self.time_unit)
            self.result.os_cpu_time += 1
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) is executing TIP")

    def execute_tcp(self, process: RunningProcess):
        for _ in range(self.scheduler.tcp):
            self.system_executor.execute_tcp_tick(process, self.time_unit)
            self.result.os_cpu_time += 1
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) is executing TCP")

    def execute_tfp(self, process: RunningProcess):
        for _ in range(self.scheduler.tfp):
            self.system_executor.execute_tfp_tick(process, self.time_unit)
            self.result.os_cpu_time += 1
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) is executing TFP")

    def execute_process(self, process: RunningProcess):
        if process.pending_cpu_burst_in_execution > 0:
            self.system_executor.execute_cpu_tick(process, self.time_unit)
            process.service_time += 1
            for i in range(1, len(self.ready_queue)):
                self.ready_queue[i].ready_wait_time += 1
            self.last_executed_process = process
            self.advance_time_unit()
            self.update_io_blocked_queue()
            self.update_ready_queue()
            self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) is executing CPU burst")
            self.quantum_counter += 1

        if process.pending_cpu_burst_in_execution == 0:
            if process.cpu_burst_count > 0:
                process.cpu_burst_count -= 1
                process.pending_cpu_burst_in_execution = process.cpu_burst_duration
                self.quantum_counter = 0
                self.quantum_expired = False
                self.io_blocked_queue.append(process)
                self.ready_queue.remove(process)
                self.logger.info(self.time_unit, 'RUNNING', f"Process '{process.name}' (pid: {process.id}) was moved to I/O Blocked Queue")
            elif process.cpu_burst_count == 0:
                self.quantum_counter = 0
                self.quantum_expired = False
                self.execute_tfp(process)
                self.finish_process(process)
        elif self.quantum_counter % self.scheduler.quantum == 0:
            self.ready_queue.remove(process)
            self.ready_queue.append(process)
            self.quantum_expired = True
            self.logger.info(self.time_unit, 'READY', f"Process '{process.name}' (pid: {process.id}) moved to end of the Ready Queue (Quantum expired)")
        process.recently_moved_to_ready_queue = False

    def finish_process(self, process: RunningProcess):
        self.result.finished_processes.append(FinishedProcess(
            **process.__dict__,
            return_instant=self.time_unit,
            return_time=self.time_unit - process.arrival_time,
            normalized_return_time=(self.time_unit - process.arrival_time) / process.service_time
        ))
        self.ready_queue.remove(process)
        self.logger.info(self.time_unit, 'FINISHED', f"Process '{process.name}' (pid: {process.id}) has finished")

    def execute(self) -> SchedulerResult:
        while len(self.result.finished_processes) < len(self.scheduler.processes):
            if not self.ready_queue:
                self.system_executor.execute_idle_tick(self.time_unit)
                self.result.idle_cpu_time += 1
                self.advance_time_unit()
                self.update_io_blocked_queue()
                self.update_ready_queue()
                self.logger.info(self.time_unit, '-', "CPU Idle")
            else:
                current_process = self.ready_queue[0]
                if (
                    (
                        self.last_executed_process != current_process
                        and self.last_executed_process is not None 
                        and current_process.tip_already_executed
                        and current_process.recently_moved_to_ready_queue
                    )
                    or (
                        self.last_executed_process == current_process
                        and current_process.recently_moved_to_ready_queue
                    )
                    or (
                        self.last_executed_process == current_process
                        and self.quantum_expired                        
                    )
                ):
                    self.execute_tcp(current_process)
                    current_process.recently_moved_to_ready_queue = False
                    self.last_executed_process = current_process
                    self.quantum_counter = 0
                    self.quantum_expired = False
                elif self.last_executed_process != current_process and not current_process.tip_already_executed:
                    self.execute_tip(current_process)
                    current_process.tip_already_executed = True
                    current_process.recently_moved_to_ready_queue = False
                    self.last_executed_process = current_process
                else:
                    self.execute_process(current_process)

        self.result.finished_processes.sort(key=lambda x: x.id)
        self.result.batch_return_time = self.time_unit
        self.result.average_batch_return_time = sum(p.return_time for p in self.result.finished_processes) / len(self.result.finished_processes)
        self.result.state_history = self.system_executor.get_history()
        return self.result