from io import TextIOWrapper
import random

from .utils import QASM_prefix, random_pauli, random_cliff3, random_cliff7, random_univeral, random_cgate, get_dagger

class Palindrome():
    def __init__(self, qubits: int, seed: int):
        self.qubits = qubits
        random.seed(seed)
        self.f: TextIOWrapper = None

    def generate(self, n_palindromes: int, n_gates: int, cgate_ratio: int, gate_set: str = "u",  filename: str = "palindrome"):
        self.f = open("circuits/"+filename+".qasm", "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        for i in range(self.qubits):
            self.f.write(f"h q[{i}];\n")
        # self.f.write("barrier;\n")
        for _ in range(n_palindromes):
            gates = []
            self.f.write("barrier;\n")
            for _ in range(n_gates):
                if(random.random() < cgate_ratio):
                    gates.append(random_cgate(self.qubits-1))
                else:
                    if(gate_set == "p"):
                        gate = random_pauli()
                    elif(gate_set == "c3"):
                        gate = random_cliff3()
                    elif(gate_set == "c7"):
                        gate = random_cliff7()
                    elif(gate_set == "u"):
                        gate = random_univeral()
                    gates.append(gate+f" q[{random.randint(0,self.qubits-2)}];\n")
                self.f.write(gates[-1])
            self.f.write("c"*(self.qubits-1)+"x "+"q["+"], q[".join([str(x) for x in range(self.qubits-1)])+f"], q[{self.qubits-1}];\n")
            for i in range(n_gates-1,-1,-1):
                gate = gates[i].split(" ")[0]
                dagger = get_dagger(gate)
                self.f.write(dagger+gates[i][len(gate):])
            self.f.write("barrier;\n")