import os
import questionary
from scheduler import Scheduler
from enums import Policy

def clearScreen() -> None:
    os.system('clear' if os.name == 'posix' else 'cls')

def get_user_input():
    policy = questionary.select(
        "Seleccione la política de planificación:",
        choices=[policy.value for policy in Policy]
    ).ask()

    tip = questionary.text(
        "Ingrese el Tiempo Inicial del Proceso (TIP):",
        validate=lambda val: val.isdigit() or "Por favor ingrese un número"
    ).ask()

    tfp = questionary.text(
        "Ingrese el Tiempo Final del Proceso (TFP):",
        validate=lambda val: val.isdigit() or "Por favor ingrese un número"
    ).ask()

    tcp = questionary.text(
        "Ingrese el Tiempo de Creación del Proceso (TCP):",
        validate=lambda val: val.isdigit() or "Por favor ingrese un número"
    ).ask()

    quantum = questionary.text(
        "Ingrese el Quantum (para Round Robin):",
        validate=lambda val: val.isdigit() or "Por favor ingrese un número"
    ).ask()

    return {
        'policy': policy,
        'tip': int(tip),
        'tfp': int(tfp),
        'tcp': int(tcp),
        'quantum': int(quantum)
    }

def main():
    clearScreen()
    
    print("Bienvenido al Planificador de Procesos")
    print("======================================\n")
    
    answers = get_user_input()
    
    policy = next(p for p in Policy if p.value == answers['policy'])
    tip = answers['tip']
    tfp = answers['tfp']
    tcp = answers['tcp']
    quantum = answers['quantum']
    
    scheduler = Scheduler()
    scheduler.execute_scheduler(policy, tip, tfp, tcp, quantum)

if __name__ == "__main__":
    main()