from enum import Enum

class Task(Enum):
    EXECUTING_CPU = 1
    WAITING_IO = 2
    WAITING_IDLE = 3
    EXECUTING_TIP = 4
    EXECUTING_TCP = 5
    EXECUTING_TFP = 6