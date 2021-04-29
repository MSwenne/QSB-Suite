from io import TextIOWrapper
from math import ceil, floor, log2
from typing import List

from .utils import QFT, QFT_inv, QASM_prefix

class Shor():
    def __init__(self, a: int,N: int):
        self.a = a
        self.N = N
        self.f: TextIOWrapper = None
        self.shor_n = ceil(log2(N))
        self.top        = 0
        self.ctrl_first = 1
        self.ctrl_last  = self.shor_n
        self.helper     = self.shor_n + 1
        self.targ_first = self.shor_n + 2
        self.targ_last  = 2*self.shor_n + 2
        self.shor_bits_a = [0]*64
        self.shor_bits_N = [0]*64
        p2 = 1
        for i in range(self.shor_n):
            self.shor_bits_a[i] = a & p2
            self.shor_bits_N[i] = N & p2
            p2 = p2 << 1

    def set_a(self, a: int) -> bool:
        if (a <= 0 or a >= self.N):
            return False
        self.a = a
        p2 = 1
        for i in range(self.shor_n):
            self.shor_bits_a[i] = a & p2
            p2 = p2 << 1
        return True

    def set_N(self, N: int) -> bool:
        if (N <= 0 or N <= self.a):
            return False
        self.N = N
        self.shor_n = ceil(log2(N))
        self.top        = 0
        self.ctrl_first = 1
        self.ctrl_last  = self.shor_n
        self.helper     = self.shor_n + 1
        self.targ_first = self.shor_n + 2
        self.targ_last  = 2*self.shor_n + 2
        p2 = 1
        for i in range(self.shor_n):
            self.shor_bits_N[i] = N & p2
            p2 = p2 << 1
        return True

    def __write_phi(self, c1: int, c2: int, qubit: int, rotation: float):
        if (c1 == -1):
            if (c2 == -1):
                self.f.write(f"rz({rotation}) q[{qubit}];\n")
            else:
                self.f.write(f"crz({rotation}) q[{c2}], q[{qubit}];\n")
        else:
            if (c2 == -1):
                self.f.write(f"crz({rotation}) q[{c1}], q[{qubit}];\n")
            else:
                self.f.write(f"ccrz({rotation}) q[{c1}], q[{c2}], q[{qubit}];\n")

    def __phi_add(self, first: int, last: int, c1: int, c2: int, a: List[bool], inverse: bool):
        num_qubits = (last - first) + 1
        parity =  -inverse*2+1
        for i in range (num_qubits):
            qubit = first + i
            for j in range(num_qubits-i):
                if (a[j]):
                    k = num_qubits-j-i
                    self.__write_phi(c1, c2, qubit, parity*1/(2**k))

    def __phi_add_mod(self, c1: int, c2: int, a: int, N: int):
        # 1.  controlled(c1,c2) phi_add(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=False)
        # 2.  phi_add_inv(N)
        self.__phi_add(self.targ_first, self.targ_last, -1, -1, self.shor_bits_N, inverse=True)
        # 3.  QFT_inv
        self.f.write(QFT_inv(self.targ_first, self.targ_last))
        # 4.  CNOT (control = carry wire? = first of phi ADD, target = helper)
        self.f.write(f"cx q[{self.targ_first}], q[{self.helper}];\n")
        # 5.  QFT
        self.f.write(QFT(self.targ_first, self.targ_last))
        # 6.  controlled phi_add(N) (control = helper)
        self.__phi_add(self.targ_first, self.targ_last, self.helper, -1, self.shor_bits_N, inverse=False)
        # 7. controlled(c1, c2) phi_add_inv(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=True)
        # 8.  QFT_inv
        self.f.write(QFT_inv(self.targ_first, self.targ_last))
        # 9.  X on same wire as control of CNOT in 4/10
        self.f.write(f"x q[{self.targ_first}];\n")
        # 10. CNOT 
        self.f.write(f"cx q[{self.targ_first}], q[{self.helper}];\n")
        # 11. X on same wire as control of CNOT in 4/10
        self.f.write(f"x q[{self.targ_first}];\n")
        # 12. QFT
        self.f.write(QFT(self.targ_first, self.targ_last))
        # 13. controlled(c1,c2) phi_add(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=False)

    def __phi_add_mod_inv(self, c1: int, c2: int, a: int, N: int):
        # 13. controlled(c1,c2) phi_add_inv(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=True)
        # 12. QFT^-1
        self.f.write(QFT_inv(self.targ_first, self.targ_last))
        # 11. X^-1 = X
        self.f.write(f"x q[{self.targ_first}];\n")
        # 10. CNOT^-1 = CNOT
        self.f.write(f"cx q[{self.targ_first}], q[{self.helper}];\n")
        # 9.  X^-1 = X
        self.f.write(f"x q[{self.targ_first}];\n")
        # 8.  (QFT^-1)^-1 = QFT
        self.f.write(QFT(self.targ_first, self.targ_last))
        # 7.  controlled(c1, c2) phi_add(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=False)
        # 6.  controlled phi_add_inv(N) (control = helper)
        self.__phi_add(self.targ_first, self.targ_last, self.helper, -1, self.shor_bits_N, inverse=True)
        # 5.  QFT^-1
        self.f.write(QFT_inv(self.targ_first, self.targ_last))
        # 4. CNOT^-1 = CNOT (control = carry wire? = first of phi ADD, target = helper)
        self.f.write(f"cx q[{self.targ_first}], q[{self.helper}];\n")
        # 3. (QFT^-1)^-1 = QFT
        self.f.write(QFT(self.targ_first, self.targ_last))
        # 2.  phi_add(N)
        self.__phi_add(self.targ_first, self.targ_last, -1, -1, self.shor_bits_N, inverse=False)
        # 1.  controlled(c1,c2) phi_add_inv(a)
        self.__phi_add(self.targ_first, self.targ_last, c1, c2, self.shor_bits_a, inverse=True)

    def __cmult(self, a: int, N: int):
        # this implements the _controlled_ cmult operation
        # 1. QFT on bottom register
        self.f.write(QFT(self.targ_first, self.targ_last))

        # 2. loop over k = {0, n-1}
        t = a
        # //BDDVAR cs[] = {self.top, QDD_INVALID_VAR, QDD_INVALID_VAR};
        for c2 in range(self.ctrl_last, self.ctrl_first-1,-1):
            # 2a. double controlled phi_add_mod(a* 2^k)
            self.__phi_add_mod(self.top, c2, t, N)
            t = (2*t) % N

        # 3. QFT^-1 on bottom register
        self.f.write(QFT_inv(self.targ_first, self.targ_last))

    def __cmult_inv(self, a: int, N: int):
        # not quite inverse of above
        # 1. QFT on bottom register
        self.f.write(QFT(self.targ_first, self.targ_last))
        
        # 2. same loop over k but with phi_add_mod_inv
        t = a
        for c2 in range(self.ctrl_last, self.ctrl_first-1,-1):
            # 2a. double controlled phi_add_mod_inv(a* 2^k)
            self.__phi_add_mod_inv(self.top, c2, t, N)
            t = (2*t) % N

        # 3. QFT^-1 on bottom register
        self.f.write(QFT(self.targ_first, self.targ_last))

    def __inverse_mod(self):
        t = 0
        newt = 1
        r = self.N
        newr = self.a
        while(newr != 0):
            quotient = floor(r / newr)
            h = t
            t = newt
            newt = h - quotient * newt
            h = r
            r = newr
            newr = h - quotient * newr
        if(r > 1):
            print("ERROR: a is not invertible.")
        if(t < 0):
            t = t + self.N
        return t

    def __shor_ua(self, a: int, N: int):
        # 1. controlled Cmult(a)
        self.__cmult(a, N)
        # 2. controlled swap top/bottom registers
        for c2 in range(self.ctrl_first, self.ctrl_last):
            t = self.targ_first+c2
            self.f.write(f"cx q[{t}], q[{c2}];\n")
            self.f.write(f"ccx q[{self.top}], q[{c2}], q[{t}];\n")
            self.f.write(f"cx q[{t}], q[{c2}];\n")

        # 3. controlled Cmult_inv(a^-1)
        a_inv = self.__inverse_mod()
        self.__cmult_inv(a_inv, N)

    def generate_2n_3(self, filename: str = "shor.txt") -> None:
        # set variables
        qubits = 2*self.shor_n+3
        ua = [0]*(2*self.shor_n)
        ua[2*self.shor_n-1] = self.a
        new_a = self.a
        for i in range(2*self.shor_n-1,-1,-1):
            new_a = new_a * new_a
            new_a = new_a % self.N
            ua[i] = new_a

        self.f = open(filename, "w")
        self.f.write(QASM_prefix(qubits, qubits))

        self.f.write(f"x q[{self.shor_n}]\n")
        for i in range(2*self.shor_n):
            self.f.write(f"h q[{0}]\n")
            self.__shor_ua(ua[i], self.N)
            k = 2
            for j in range(i-1,-1,-1):
                # if (outcomes[j] == 1):
                self.f.write(f"rz({1/(2**k)}) q[{self.top}];\n")
                k += 1
            self.f.write(f"h q[{0}]\n")
        self.f.close()
        return True

    def generate(self, filename: str = "shor.txt") -> None:
        return True

