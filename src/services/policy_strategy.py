from abc import ABC, abstractmethod
from typing import List
from models import ProcessScheduler, SchedulerResult, RunningProcess
from system import System

class PolicyStrategy(ABC):
    def __init__(self, scheduler: ProcessScheduler):
        self.scheduler = scheduler

        self.time_unit = 0
        self.ready_queue: List[RunningProcess] = []
        self.io_blocked_queue: List[RunningProcess] = []
        self.last_executed_process_id = -1
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

    def advance_time_unit(self):
        self.time_unit += 1

    def update_io_blocked_queue(self):
        processes_reviewed = 0
        while processes_reviewed < len(self.io_blocked_queue):
            process = self.io_blocked_queue[processes_reviewed]
            if process.pending_io_burst_in_execution > 0:
                self.system_executor.execute_io_tick(process, self.time_unit)

            if process.pending_io_burst_in_execution == 0:
                if process.io_burst_count > 0:
                    process.io_burst_count -= 1
                    process.pending_io_burst_in_execution = process.io_burst_duration

                self.ready_queue.append(process)
                self.io_blocked_queue.pop(processes_reviewed)
            else:
                processes_reviewed += 1

    @abstractmethod
    def execute(self) -> SchedulerResult:
        pass
