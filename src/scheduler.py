from typing import List
import csv
from models import ProcessScheduler, Process
from services import FCFS, RoundRobin, ExternalPriority, SPN, SRTN
from enums import Policy
from tools import CustomLogger

class Scheduler:
    def __init__(self):
        self.policies = {
            Policy.FCFS: FCFS,
            Policy.RR: RoundRobin,
            Policy.EP: ExternalPriority,
            Policy.SPN: SPN,
            Policy.SRTN: SRTN,
        }
        self.logger = None

    @staticmethod
    def __load_processes_from_file(file_path: str) -> List[Process]:
        processes = []
        try:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                pid = 0
                for row in reader:
                    if len(row) != 6:
                        print(f"Error: La fila {row} no tiene el formato esperado.")
                        continue
                    pid += 1
                    process = Process(
                        id=pid,
                        name=row[0],
                        arrival_time=int(row[1]),
                        cpu_burst_count=int(row[2]),
                        cpu_burst_duration=int(row[3]),
                        io_burst_count=int(row[2]),
                        io_burst_duration=int(row[4]),
                        priority=int(row[5])
                    )
                    processes.append(process)
        except FileNotFoundError:
            print(f"Error: El archivo '{file_path}' no se encontró.")
        except Exception as e:
            print(f"Error al leer el archivo '{file_path}': {e}")
        return processes

    def execute_scheduler(self, policy: Policy, tip: int, tfp: int, tcp: int, quantum: int) -> None:
        processes = self.__load_processes_from_file('data/processes.txt')
        process_scheduler = ProcessScheduler(policy, processes, tip, tfp, tcp, quantum)

        self.logger = CustomLogger(policy.value)
        self.logger.log_parameters(process_scheduler)

        policy = process_scheduler.policy
        if policy not in self.policies:
            raise ValueError(f'Error en política seleccionada: {policy.value} - Falta implementación')

        executor = self.policies[policy](process_scheduler, self.logger)
        result = executor.execute()
        
        self.logger.log_summary(result)

        print('\n')
        print('===========================Resultado===============================\n')
        print(result)
        print('\n===================================================================')