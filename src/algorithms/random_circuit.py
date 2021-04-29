from io import TextIOWrapper
import random

from .utils import QASM_prefix

class Random_circuit():
    def __init__(self, qubits: int, seed: int = 42):
        random.seed(seed)
        self.qubits = qubits
        self.f: TextIOWrapper = None

    def set_seed(self, seed: int) -> None:
        random.seed(seed)

    def __random_pauli(self) -> str:
        return random.choice(["x", "y", "z"])

    def __random_cliff3(self):
        return random.choice(["x", "h", "s"])


    def __random_cliff7(self):
        return random.choice(["x", "y", "z", "h", "sx", "sy", "s"])


    def __random_univeral(self):
        return random.choice(["x", "y", "z", "h", "t"])

    def __random_cgate(self):
        c = random.randint(0,self.qubits-1)
        t = random.randint(0,self.qubits-1)
        while c == t:
            t = random.randint(0,self.qubits-1)
        self.f.write(f"cz q[{c}], q[{t}];\n")

    def generate(self, n_gates: int, cgate_ratio: int, gate_set: str = "u", filename: str = "random.txt"):
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        for _ in range(n_gates):
            if(random.random() < cgate_ratio):
                self.__random_cgate()
            else:
                if(gate_set == "p"):
                    gate = self.__random_pauli()
                elif(gate_set == "c3"):
                    gate = self.__random_cliff3()
                elif(gate_set == "c7"):
                    gate = self.__random_cliff7()
                elif(gate_set == "u"):
                    gate = self.__random_univeral()
                self.f.write(gate+f" q[{random.randint(0,self.qubits-1)}];\n")
        self.f.close()