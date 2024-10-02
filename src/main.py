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

    def validate_positive_integer(val):
        if not val.isdigit():
            return "Por favor ingrese un número entero positivo"
        if int(val) <= 0:
            return "El valor debe ser mayor que 0"
        return True

    tip = questionary.text(
        "Ingrese el TIP:",
        validate=validate_positive_integer
    ).ask()

    tcp = questionary.text(
        "Ingrese el TCP:",
        validate=validate_positive_integer
    ).ask()

    tfp = questionary.text(
        "Ingrese el TFP:",
        validate=validate_positive_integer
    ).ask()

    quantum = None
    if policy == Policy.RR.value:
        def validate_quantum(val):
            if not val.isdigit():
                return "Por favor ingrese un número entero positivo"
            quantum_value = int(val)
            if quantum_value <= 0:
                return "El Quantum debe ser mayor que 0"
            if quantum_value <= int(tip):
                return f"El Quantum debe ser mayor que el TIP ({tip})"
            if quantum_value <= int(tcp):
                return f"El Quantum debe ser mayor que el TCP ({tcp})"
            if quantum_value <= int(tfp):
                return f"El Quantum debe ser mayor que el TFP ({tfp})"
            return True

        quantum = questionary.text(
            "Ingrese el Quantum:",
            validate=validate_quantum
        ).ask()

    return {
        'policy': policy,
        'tip': int(tip),
        'tcp': int(tcp),
        'tfp': int(tfp),
        'quantum': int(quantum) if quantum is not None else None
    }

def main():
    clearScreen()
    
    print("Bienvenido al Planificador de Procesos")
    print("======================================\n")
    
    answers = get_user_input()
    
    policy = next(p for p in Policy if p.value == answers['policy'])
    tip = answers['tip']
    tcp = answers['tcp']
    tfp = answers['tfp']
    quantum = answers['quantum']
    
    scheduler = Scheduler()
    scheduler.execute_scheduler(policy, tip, tfp, tcp, quantum)

if __name__ == "__main__":
    main()