from io import TextIOWrapper

from .utils import QASM_prefix, QFT, QFT_inv

class Adder():
    def __init__(self, qubits_a: int, qubits_b: int):
        self.n_a = qubits_a
        self.n_b = qubits_b
        self.f: TextIOWrapper = None

    def generate(self, a: int, b: int, filename: str = "adder.txt"):
        a_bin = [a >> i & 1 for i in range(self.n_a)]
        b_bin = [b >> i & 1 for i in range(self.n_b)]
        self.f = open(filename, "w")
        self.f.write(QASM_prefix(self.n_a+self.n_b, self.n_a+self.n_b))
        for i in range(self.n_a):
            if a_bin[i]: self.f.write(f"x q[{i}];\n")
        for i in range(self.n_b):
            if b_bin[i]: self.f.write(f"x q[{self.n_a+i}];\n")
        self.f.write("\n")
        self.f.write(QFT(self.n_a, self.n_a+self.n_b-1))
        self.f.write("\n// Begin adder\n")
        for i in range(self.n_a):
            k = 1
            for j in range(self.n_b-(self.n_a-i)+1, 0, -1):
                self.f.write(f"crz({1/pow(2,k)}) q[{i}], q[{self.n_a+j-1}];\n")
                k+=1
        self.f.write("\n")
        self.f.write(QFT_inv(self.n_a, self.n_a+self.n_b-1))
        self.f.write("\n")
        for i in range(self.n_a+self.n_b):
            self.f.write(f"measure q[{i}]->c[{i}];\n")