from io import TextIOWrapper
from typing import List
import random

from .utils import QASM_prefix

class Supremacy():
    def __init__(self, seed: int = 42, barrier: bool = True):
        random.seed(seed)
        self.barrier = barrier
        self.f: TextIOWrapper = None

    def set_seed(self, seed: int) -> None:
        random.seed(seed)

    def __write_random_sqrtXYs(self, tgts: List[int]) -> None:
        for tgt in tgts:
            if (random.random() >= 0.5):
                self.f.write(f"sx q[{tgt}];\n")
            else:
                self.f.write(f"sy q[{tgt}];\n")

    def __write_CZs(self, ctrls: List[int], tgts: List[int]) -> None:
        for ctrl, tgt in zip(ctrls,tgts):
            self.f.write(f"cz q[{ctrl}], q[{tgt}];\n")

    def __write_Ts(self, tgts: List[int]) -> None:
        for tgt in tgts:
            self.f.write(f"t q[{tgt}];\n")

    def generate_5_1(self, depth: int, filename: str = "supremacy.txt") -> None:
        self.qubits = 5
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))
        for i in range(self.qubits):
            self.f.write(f"h q[{i}];\n")
        if (self.barrier):
            self.f.write(f"barrier;\n")
        if (depth > 0):
            self.f.write(f"// Depth 1\n")
            self.__write_CZs(ctrls=[0,3], tgts=[1,4])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 1):
            self.f.write(f"// Depth 2\n")
            self.__write_CZs(ctrls=[1], tgts=[2])
            self.__write_Ts(tgts=[1,3,4])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 2):
            self.f.write(f"// Depth 3\n")
            self.__write_CZs(ctrls=[2], tgts=[3])
            self.__write_Ts(tgts=[1])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 3):
            self.f.write(f"// Depth 4\n")
            self.__write_CZs(ctrls=[0,3], tgts=[1,4])
            self.__write_Ts(tgts=[2])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        # Following cycles the single qubit gates are random from:sqrt(X), sqrt(Y)}
        for i in range(4,depth):
            self.f.write(f"// Depth {i+1}\n")
            if (i % 3 == 0):
                self.__write_CZs(ctrls=[0,3], tgts=[1,4])
                self.__write_random_sqrtXYs(tgts=[2])
            elif (i % 3 == 1):
                self.__write_CZs(ctrls=[1], tgts=[2])
                self.__write_random_sqrtXYs(tgts=[0,3,4])
            elif (i % 3 == 2):
                self.__write_CZs(ctrls=[2], tgts=[3])
                self.__write_random_sqrtXYs(tgts=[0,1,4])
            if (self.barrier):
                    self.f.write(f"barrier;\n")
        self.f.close()

    def generate_5_4(self, depth: int, filename: str = "supremacy.txt") -> None:
        # 5x4 "grid" from [Characterizing Quantum Supremacy in Near-Term Devices]
        # (maybe a lot of hard-coded stuff but oh well...)

        # Start with |00...0> state
        self.qubits = 20
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.qubits, self.qubits))

        # H on all qubits
        for i in range(self.qubits):
            self.f.write(f"h q[{i}];\n")
        if (self.barrier):
            self.f.write(f"barrier;\n")

        # First 7 cycles the single qubit gates we apply are all T gates
        # (not sure if we also should do random:sqrt(X), sqrt(Y)} on the
        # remaining qubits, the paper is not super clear)
        if (depth > 0):
            self.f.write(f"// Depth 1\n")
            self.__write_CZs(ctrls=[2,5,12,15], tgts=[3,6,13,16])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 1):
            self.f.write(f"// Depth 2\n")
            self.__write_CZs(ctrls=[0,7,10,17], tgts=[1,8,11,18])
            self.__write_Ts(tgts=[2,3,5,6,12,13,15,16])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 2):
            self.f.write(f"// Depth 3\n")
            self.__write_CZs(ctrls=[6,8], tgts=[11,13])
            self.__write_Ts(tgts=[0,1,7,8,10,11,17,18])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 3):
            self.f.write(f"// Depth 4\n")
            self.__write_CZs(ctrls=[5,7,9], tgts=[10,12,14])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 4):
            self.f.write(f"// Depth 5\n")
            self.__write_CZs(ctrls=[3,6,13,16], tgts=[4,7,14,17])
            self.__write_Ts(tgts=[9,14])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 5):
            self.f.write(f"// Depth 6\n")
            self.__write_CZs(ctrls=[1,8,11,18], tgts=[2,9,12,19])
            self.__write_Ts(tgts=[4])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        if (depth > 6):
            self.f.write(f"// Depth 7\n")
            self.__write_CZs(ctrls=[0,2,4,11,13], tgts=[5,7,9,16,18])
            self.__write_Ts(tgts=[9])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        # Following cycles the single qubit gates are random from:sqrt(X), sqrt(Y)}
        for i in range(7,depth):
            self.f.write(f"// Depth {i+1}\n")
            if (i % 8 == 0):
                self.__write_CZs(ctrls=[2,5,12,15], tgts=[3,6,13,16])
                self.__write_random_sqrtXYs([1,8,10,14,17,19])
            elif (i % 8 == 1):
                self.__write_CZs(ctrls=[0,7,10,17], tgts=[1,8,11,18])
                self.__write_random_sqrtXYs([2,3,5,6,12,13,15,16])
            elif (i % 8 == 2):
                self.__write_CZs(ctrls=[6,8], tgts=[11,13])
                self.__write_random_sqrtXYs([0,1,7,10,17,18])
            elif (i % 8 == 3):
                self.__write_CZs(ctrls=[5,7,9], tgts=[10,12,14])
                self.__write_random_sqrtXYs([6,8,11,13])
            elif (i % 8 == 4):
                self.__write_CZs(ctrls=[3,6,13,16], tgts=[4,7,14,17])
                self.__write_random_sqrtXYs([5,9,10,12])
            elif (i % 8 == 5):
                self.__write_CZs(ctrls=[1,8,11,18], tgts=[2,9,12,19])
                self.__write_random_sqrtXYs([3,4,6,7,13,14,16,17])
            elif (i % 8 == 6):
                self.__write_CZs(ctrls=[0,2,4,11,13], tgts=[5,7,9,16,18])
                self.__write_random_sqrtXYs([1,8,12,19])
            elif (i % 8 == 7):
                self.__write_CZs(ctrls=[1,3,10,12,14], tgts=[1,8,15,17,19])
                self.__write_random_sqrtXYs([0,2,4,5,7,9,11,13,16,18])
            if (self.barrier):
                self.f.write(f"barrier;\n")
        self.f.close()