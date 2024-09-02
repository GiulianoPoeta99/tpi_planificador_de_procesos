from enum import Enum

class StateProcess(Enum):
    NEW = 1
    READY = 2
    RUNNIG = 3
    LOCKED = 4
    FINISHED = 5