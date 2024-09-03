from abc import ABC, abstractmethod
from models import ProcessScheduler, SchedulerResult

class PolicyStrategy(ABC):
    def __init__(self, scheduler: ProcessScheduler):
        self.scheduler = scheduler

    @abstractmethod
    def execute(self) -> SchedulerResult:
        pass

    def advance_time_unit(self):
        self.time_unit += 1