from abc import ABC, abstractmethod
from models import SchedulerResult

class PolicyStrategy(ABC):
    @abstractmethod
    def execute(self) -> SchedulerResult:
        pass