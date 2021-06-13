import random

def QFT(first: int, last: int) -> str:
    res = "// Begin QFT\n"
    for a in range(first, last+1):
        res += f"h q[{a}];\n"
        for b in range(a+1,last+1):
            res += f"crz({1/(2**(b-a+1))}) q[{a}], q[{b}];\n"
    return res

def QFT_inv(first: int, last: int) -> str:
    res = "// Begin QFT inverse\n"
    for a in range(last, first-1, -1):
        for b in range(last,a,-1):
            res += f"crz({-1/(2**(b-a+1))}) q[{a}], q[{b}];\n"
        res += f"h q[{a}];\n"
    return res

def QASM_prefix(qubits: int, bits: int) -> str:
    # Initial QASM setup
    res = "OPENQASM 2.0;\n"
    res += "include \"qelib1.inc\";\n\n"
    res += f"qreg q[{qubits}];\n"
    res += f"creg c[{bits}];\n\n"
    return res


def random_pauli() -> str:
    return random.choice(["x", "y", "z"])

def random_cliff3() -> str:
    return random.choice(["x", "h", "s"])

def random_cliff7() -> str:
    return random.choice(["x", "y", "z", "h", "sx", "sy", "s"])

def random_univeral() -> str:
    return random.choice(["x", "y", "z", "h", "t"])

def random_cgate(qubits):
    c = random.randint(0,qubits-1)
    t = random.randint(0,qubits-1)
    while c == t:
        t = random.randint(0,qubits-1)
    return f"cz q[{c}], q[{t}];\n"
