from io import TextIOWrapper
from typing import List
import random

from .utils import QASM_prefix

class VQC():
    def __init__(self, qubits: int, parametrized_layers: int, entanglement_layers: int = 2, gates: List[str] = ['ry', 'rz']):
        self.qubits: int = qubits
        self.entanglement_layers: int = entanglement_layers
        self.parametrized_layers: int = parametrized_layers
        self.gates: List[str] = gates
        self.circuit: List[str] = []
        self.create_circuit()
        self.f: TextIOWrapper = None

    def create_circuit(self) -> None:
        # Entangle datapoint
        for _ in range(self.entanglement_layers):
            for i in range(self.qubits):
                self.circuit.append(f"h q[{i}];\n")
            for i in range(self.qubits):
                self.circuit.append("rz({})"+f" q[{i}];\n")
            for i in range(self.qubits-1):
                for j in range(i+1,self.qubits):
                    self.circuit.append("crz({})"+f" q[{i}], q[{j}];\n")
        # Parametrized gates
        for gate in self.gates:
            for i in range(self.qubits):
                self.circuit.append(f"{gate}"+"({})"+f" q[{i}];\n")
        for _ in range(self.parametrized_layers):
            for i in range(self.qubits-1):
                self.circuit.append(f"cz q[{i}], q[{i+1}];\n")
            if (self.qubits != 2):
                self.circuit.append(f"cz q[{0}], q[{self.qubits-1}];\n")
            for gate in self.gates:
                for i in range(self.qubits):
                    self.circuit.append(f"{gate}"+"({})"+f" q[{i}];\n")
        for i in range(self.qubits):
            self.circuit.append(f"measure q[{i}]->c[{i}];\n")

    def generate(self, datapoint: List[float], theta: List[float], filename: str = "vqc.txt") -> None:
        # Create entangled rotations for every qubit pair
        entangled_rot = []
        for i in range(self.qubits-1):
            for j in range(i+1, self.qubits):
                entangled_rot.append((1-datapoint[i])*(1-datapoint[j]))
        # Collect all values to be inserted
        params = []
        for i in range(self.entanglement_layers):
            params.extend(datapoint)
            params.extend(entangled_rot)
        params.extend(theta)
        # Fill in all values and write to file
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        j = 0
        for line in self.circuit:
            if (line.find('{}') != -1):
                self.f.write(line.format(round(params[j]%1.0, 6)))
                j += 1
            else:
                self.f.write(line)
        self.f.close()
        return True

    def generate_random(self, seed: int = 42, filename: str = "vqc.txt") -> None:
        random.seed(seed)
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        j = 0
        for line in self.circuit:
            if (line.find('{}') != -1):
                self.f.write(line.format(round(random.random()%1.0, 6)))
                j += 1
            else:
                self.f.write(line)
        self.f.close()
        return True
