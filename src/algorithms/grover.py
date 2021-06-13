from io import TextIOWrapper
from math import floor, sqrt, pi
from typing import List

from .utils import QASM_prefix

class Grover():
    def __init__(self, qubits: int, barrier: bool = True):
        self.qubits: int = qubits
        self.f: TextIOWrapper = None

    def set_qubits(self, qubits: int) -> bool:
        if (qubits <= 0):
            return False
        self.qubits = qubits
        return True

    def __write_measure(self) -> None:
        ''' 
        Writes QASM measure gates to <f> for Grover's algorithm using <qubits> qubits
        - f: TextIOWrapper to write the QASM to
        - qubits: the number of qubits that need to be measured
        '''
        self.f.write(f"\n// Begin measure\n")
        for i in range(self.qubits):
            self.f.write(f"measure q[{i}] -> c[{i}];\n")

    def __write_mean_inversion(self) -> None:
        ''' 
        Writes QASM gates to <f> needed for Grover's algorithm mean inversion using <qubits> qubits
        - f: TextIOWrapper to write the QASM to
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        '''
        self.f.write(f"\n// Begin mean inversion\n")
        self.f.write(f"barrier;\n")
        for i in range(self.qubits):
            self.f.write(f"h q[{i}];\n")
        for i in range(self.qubits):
            self.f.write(f"x q[{i}];\n")
        self.f.write("c"*self.qubits+"x "+"q["+"], q[".join([str(x) for x in range(self.qubits+1)])+"];\n")
        for i in range(self.qubits):
            self.f.write(f"x q[{i}];\n")
        for i in range(self.qubits):
            self.f.write(f"h q[{i}];\n")
        self.f.write(f"barrier;\n")

    def __write_oracle(self, oracle: List[int]) -> None:
        ''' 
        Writes QASM gates to <f> needed for Grover's algorithm oracle using <qubits> qubits
        - f: TextIOWrapper to write the QASM to
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        - oracle: the oracle we need to find with Grover's algorithm
        '''
        self.f.write(f"// Begin oracle\n")
        self.f.write(f"barrier;\n")
        for i, bit in enumerate(oracle):
            if not bit: self.f.write(f"x q[{i}];\n")
        self.f.write("c"*self.qubits+"x "+"q["+"], q[".join([str(x) for x in range(self.qubits+1)])+"];\n")
        for i, bit in enumerate(oracle):
            if not bit: self.f.write(f"x q[{i}];\n")
        self.f.write(f"barrier;\n")

    def __write_oracle_kSAT(self, kSAT: int, oracle: List[int]) -> None:
        ''' 
        Writes QASM gates to <f> needed for Grover's algorithm oracle using <qubits> qubits
        - f: TextIOWrapper to write the QASM to
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        - kSAT: the number of qubits per clause in the k-SAT cnf
        - oracle: the oracle we need to find with Grover's algorithm
        '''
        clauses = int(len(oracle) / kSAT)
        targets = [str(abs(x)-1) for x in oracle]
        self.f.write(f"// Begin oracle\n")
        self.f.write(f"barrier;\n")
        for clause in range(clauses):
            for i in oracle[clause*kSAT:(clause+1)*kSAT]:
                if i < 0: self.f.write(f"x q[{abs(i+1)}];\n")
            self.f.write(f"{'c'*kSAT}x q[{'], q['.join(targets[clause*kSAT:(clause+1)*kSAT])}], q[{self.qubits+1+clause}];\n")
            for i in oracle[clause*kSAT:(clause+1)*kSAT]:
                if i < 0: self.f.write(f"x q[{abs(i+1)}];\n")
        for i in range(self.qubits,self.qubits+clauses):
            self.f.write(f"x q[{abs(i+1)}];\n")
        self.f.write("c"*clauses+"x "+"q["+"], q[".join([str(x) for x in range(self.qubits+1,self.qubits+1+clauses)])+f"], q[{self.qubits}];\n")
        for i in range(self.qubits,self.qubits+clauses):
            self.f.write(f"x q[{abs(i+1)}];\n")
        for clause in range(clauses-1,-1,-1):
            for i in oracle[clause*kSAT:(clause+1)*kSAT]:
                if i < 0: self.f.write(f"x q[{abs(i+1)}];\n")
            self.f.write(f"{'c'*kSAT}x q[{'], q['.join(targets[clause*kSAT:(clause+1)*kSAT])}], q[{self.qubits+1+clause}];\n")
            for i in oracle[clause*kSAT:(clause+1)*kSAT]:
                if i < 0: self.f.write(f"x q[{abs(i+1)}];\n")
        self.f.write(f"barrier;\n")

    def __write_init(self) -> None:
        ''' 
        Writes QASM gates to <f> needed for Grover's algorithm initialisation using <qubits> qubits
        - f: TextIOWrapper to write the QASM to
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        '''
        self.f.write(f"// Begin init\n")
        self.f.write(f"x q[{self.qubits}];\n")
        for i in range(self.qubits+1):
            self.f.write(f"h q[{i}];\n")
        self.f.write(f"barrier;\n")

    def __get_iterations(self, n_answers: int) -> int:
        return floor(pi/4*sqrt(2**self.qubits/n_answers))

    def __get_bin_oracle(self, oracle: int) -> List[int]:
        oracle = [oracle >> i & 1 for i in range(self.qubits-1,-1,-1)]
        return oracle[::-1]

    def generate(self, oracle: int, filename: str = "grover.txt") -> bool:
        ''' 
        Creates a file <filename> and writes QASM code representing Grover's algorithm
        working on <qubits> qubits (without ancillas) and having <oracle> as oracle
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        - oracle: the oracle we need to find with Grover's algorithm
        - filename: the name which the created file should get
        '''
        # Check if the oracle is valid
        iterations = self.__get_iterations(n_answers=1)
        oracle = self.__get_bin_oracle(oracle)

        self.f = open(filename, "w")
        self.f.write(QASM_prefix(qubits=self.qubits+1, bits=self.qubits))

        self.__write_init()
        for iter in range(iterations):
            self.f.write(f"\n// Iteration {iter+1}\n")
            self.__write_oracle(oracle)
            self.__write_mean_inversion()
        self.__write_measure()
        self.f.close()
        return True

    def generate_kSAT(self, oracle: List[int], kSAT: int, n_answers: int, filename: str= "grover_kSAT.txt") -> bool:
        ''' 
        Creates a file <filename> and writes QASM code representing Grover's algorithm working on <qubits> \\
        qubits (without ancillas) and having <oracle> as oracle
        - qubits: the number of qubits that Grover's algorithm uses (without ancillas)
        - kSAT: the number of qubits per clause in the k-SAT cnf
        - oracle: the oracle (in k-SAT form) we need to find with Grover's algorithm
        - n_answers: the number of answers the k-SAT cnf has (needed for calculating #iterations)
        - filename: the name which the created file should get
        '''
        iterations = self.__get_iterations(n_answers=n_answers)
        clauses = int(len(oracle) / kSAT)

        self.f = open(filename, "w")
        self.f.write(QASM_prefix(qubits=self.qubits+1+clauses, bits=self.qubits))

        self.__write_init()
        for iter in range(iterations):
            self.f.write(f"\n// Iteration {iter+1}\n")
            self.__write_oracle_kSAT(kSAT=kSAT, oracle=oracle)
            self.__write_mean_inversion()
        self.__write_measure()

        self.f.close()
        return True

