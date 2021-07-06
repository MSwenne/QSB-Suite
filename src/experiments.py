import numpy as np
import subprocess
import json
import os
from algorithms import *

# Initialisation of some parameters
seed = 42               # Random seed
np.random.seed(seed)    # Initialising random seed
limit = "80"

def gather_nodecount(filename: str, file_out: str, type: str, i, seed):
    print(f"\n{filename} nodecount: {type}")
    params = ["../../sylvan-qdd/build/parser/circuit_to_Sylvan", filename+".qasm", "-e", "-s", seed]
    if type == "greedy":
        params.append("-g")
    if type == "relationBased":
        params.append("-m")
        params.append(limit)
    if type == "balanced":
        params.append("-b")
        params.append(limit)
    # run circuit
    output = subprocess.run(params, stdout=subprocess.PIPE)
    output = output.stdout.decode('utf-8')
    output = output.split("\n")[:-1]
    output.insert(0, type+"_"+str(i))
    with open(file_out+".txt", "a") as f:
        f.write(json.dumps(output))
        f.write("\n")

def gather_time(filename: str, file_out: str, type: str, seed, i):
    params = ["../../sylvan-qdd/build/parser/circuit_to_Sylvan", filename+".qasm", "-t", "-s", seed]
    if type == "greedy_time":
        params.append("-g")
    if type == "relationBased":
        params.append("-m")
        params.append(limit)
    if type == "balanced":
        params.append("-b")
        params.append(limit)

    # run circuit
    outputs = []
    for x in range(10):
        print(f"{filename} time: {type} {(x+1):02d}",end="\r")
        output = subprocess.run(params, stdout=subprocess.PIPE)
        output = output.stdout.decode('utf-8')
        output = output.split("\n")[:-1]
        for out in output:
            if out.startswith("seconds"):
                outputs.append(out)
    outputs.insert(0, type+"_"+str(i))
    with open(file_out+".txt", "a") as f:
        f.write(json.dumps(outputs))
        f.write("\n")

def generate(alg, qubits, seed):
    if alg == "grover":
        grover = Grover(qubits=qubits)
        grover.generate(oracle=seed)
    elif alg == "grover_KSAT":
        grover_KSAT = Grover(qubits=qubits)
        oracle = [1, 2, 3,  1, 2,-3,  1,-2, 3,  -1, 2, 3,  1,-2,-3,  -1, 2,-3,  -1,-2, 3]
        for i in range(4,qubits+1):
            oracle.append(-1)
            oracle.append(-2)
            oracle.append(i)
        grover_KSAT.generate_kSAT(oracle=oracle, kSAT=3, n_answers=1)
    elif alg == "palindrome":
        palindrome = Palindrome(qubits=qubits, seed=seed)
        palindrome.generate(n_palindromes=5,n_gates=20,cgate_ratio=0.3, gate_set="u")
    elif alg == "shor":
        shor = Shor(a=7,N=15)
        shor.generate()
    elif alg == "supremacy":
        supremacy = Supremacy(seed=seed)
        supremacy.generate_5_4(depth=qubits)
    elif alg == "vqc":
        vqc = VQC(qubits=qubits,entanglement_layers=3,parametrized_layers=3)
        vqc.generate_random(seed=seed)
    else:
        print("error error")

if __name__ == '__main__':
    filenames = ["grover","grover_KSAT","palindrome","supremacy","vqc"]
    types = ["successorState","relationBased","greedy","balanced"]
    ranges = [(5,21),(5,21),(15,41),(5,21),(5,21)]
    seeds = [np.random.randint(0,1000) for _ in range(10)]
    for x, filename in enumerate(filenames):
        for type in types:
            if os.path.exists("data/"+filename+"/"+filename+"_"+type+".txt"):
                os.remove("data/"+filename+"/"+filename+"_"+type+".txt")
            if os.path.exists("data/"+filename+"/"+filename+"_"+type+"_time.txt"):
                os.remove("data/"+filename+"/"+filename+"_"+type+"_time.txt")
            for i in range(ranges[x][0],ranges[x][1]):
                for s in seeds:
                    print(i,seed)
                    print(f"\nqubits {i}" ,end="")
                    generate(filename, i, s)
                    gather_nodecount("circuits/"+filename, "data/"+filename+"/"+filename+"_"+type, type, i, str(seed))
                    gather_time("circuits/"+filename, "data/"+filename+"/"+filename+"_"+type+"_time", type, str(seed), i)
