from typing import List, Tuple
from src.models.process import Process
from src.schedulers.base_scheduler import Scheduler
from src.schedulers import FCFS, Priority, RoundRobin, SPN, SRTN

class Simulator:
    def __init__(self, input_file: str, policy: str, parameters: dict):
        self.input_file = input_file
        self.policy = policy
        self.parameters = parameters
        self.processes: List[Process] = []
        self.events: List[Tuple[int, str, Process]] = []

    def load_processes(self):
        with open(self.input_file, 'r') as file:
            for line in file:
                # Split the line into fields
                fields = line.strip().split(',')
                
                # Create a new Process object
                process = Process(
                    name=fields[0],
                    arrival_time=int(fields[1]),
                    cpu_bursts=int(fields[2]),
                    cpu_burst_duration=int(fields[3]),
                    io_burst_duration=int(fields[4]),
                    priority=int(fields[5])
                )
                
                # Set the remaining CPU time
                process.remaining_cpu_time = process.cpu_bursts * process.cpu_burst_duration
                
                # Add the process to the list
                self.processes.append(process)
        
        # Sort processes by arrival time
        self.processes.sort(key=lambda p: p.arrival_time)

    def simulate(self):
        self.load_processes()
        scheduler = self.create_scheduler()
        scheduler.run()
        self.generate_report()

    def create_scheduler(self) -> Scheduler:
        if self.policy == "FCFS":
            return FCFS(self.processes)
        elif self.policy == "Priority":
            return Priority(self.processes)
        elif self.policy == "RoundRobin":
            quantum = self.parameters.get("quantum", 1)
            return RoundRobin(self.processes, quantum)
        elif self.policy == "SPN":
            return SPN(self.processes)
        elif self.policy == "SRTN":
            return SRTN(self.processes)
        else:
            raise ValueError(f"Unrecognized scheduling policy: {self.policy}")

    def generate_report(self):
        total_turnaround_time = 0
        total_waiting_time = 0
        num_processes = len(self.processes)

        print("\nSimulation Report:")
        print("------------------")
        for process in self.processes:
            print(f"Process {process.name}:")
            print(f"  Turnaround Time: {process.turnaround_time}")
            print(f"  Waiting Time: {process.waiting_time}")
            total_turnaround_time += process.turnaround_time
            total_waiting_time += process.waiting_time

        avg_turnaround_time = total_turnaround_time / num_processes
        avg_waiting_time = total_waiting_time / num_processes

        print("\nOverall Statistics:")
        print(f"  Average Turnaround Time: {avg_turnaround_time:.2f}")
        print(f"  Average Waiting Time: {avg_waiting_time:.2f}")