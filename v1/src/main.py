from src.simulator.simulator import Simulator

def main():
    input_file = "data/processes.txt"
    
    policies = ["FCFS", "Priority", "RoundRobin"]
    
    for policy in policies:
        print(f"\nRunning simulation with {policy} policy:")
        parameters = {"quantum": 2} if policy == "RoundRobin" else {}
        
        simulator = Simulator(input_file, policy, parameters)
        simulator.simulate()

if __name__ == "__main__":
    main()