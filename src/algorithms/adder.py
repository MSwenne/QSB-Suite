from io import TextIOWrapper

from .utils import QASM_prefix, QFT, QFT_inv

class Adder():
    def __init__(self, qubits_a: int, qubits_b: int):
        self.n_a = qubits_a
        self.n_b = qubits_b
        self.f: TextIOWrapper = None

    def generate(self, a: int, b: int, filename: str = "adder"):
        a_bin = [a >> i & 1 for i in range(self.n_a)]
        b_bin = [b >> i & 1 for i in range(self.n_b)]
        self.f = open("circuits/"+filename+".qasm", "w")
        self.f.write(QASM_prefix(self.n_a+self.n_b, self.n_a+self.n_b))
        for i in range(self.n_a):
            if a_bin[i]: 
                self.f.write(f"x q[{i}];\n")
        for i in range(self.n_b):
            if b_bin[i]: 
                self.f.write(f"x q[{self.n_a+i}];\n")
        self.f.write("\n")
        self.f.write(QFT(0, self.n_a-1))
        self.f.write("\n// Begin adder\n")
        x = 0
        for i in range(self.n_a+self.n_b-1,self.n_a-1,-1):
            k = 1
            x += 1
            for j in range(self.n_a-x, self.n_a):
                if (j >= 0):
                    self.f.write(f"crz({1/pow(2,k)}) q[{i}], q[{j}];\n")
                    k += 1
        self.f.write("\n")
        self.f.write(QFT_inv(0, self.n_a-1))
        self.f.write("\n")
        for i in range(self.n_a+self.n_b):
            self.f.write(f"measure q[{i}]->c[{i}];\n")
