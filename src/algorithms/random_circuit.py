from io import TextIOWrapper
import random

from .utils import QASM_prefix, random_pauli, random_cliff3, random_cliff7, random_univeral, random_cgate

class Random_circuit():
    def __init__(self, qubits: int, seed: int = 42):
        random.seed(seed)
        self.qubits = qubits
        self.f: TextIOWrapper = None

    def set_seed(self, seed: int) -> None:
        random.seed(seed)

    def generate(self, n_gates: int, cgate_ratio: int, gate_set: str = "u", filename: str = "random"):
        if (not (gate_set in ["p", "c3", "c7", "u"])):
            print(f"Random circuit: gate set unknown: {gate_set}")
        self.f = open("circuits/"+filename+".qasm", "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        for _ in range(n_gates):
            if(random.random() < cgate_ratio):
                self.f.write(random_cgate(self.qubits))
            else:
                if(gate_set == "p"):
                    gate = random_pauli()
                elif(gate_set == "c3"):
                    gate = random_cliff3()
                elif(gate_set == "c7"):
                    gate = random_cliff7()
                elif(gate_set == "u"):
                    gate = random_univeral()
                self.f.write(gate+f" q[{random.randint(0,self.qubits-1)}];\n")
        self.f.close()