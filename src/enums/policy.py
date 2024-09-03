from enum import Enum

class Policy(Enum):
    FCFS = "First-Come, First-Served"
    RR = "Round Robin"
    SPN = "Shortest Process Next"
    SRTN = "Shortest Remaining Time Next"
    EP = "External Priority"