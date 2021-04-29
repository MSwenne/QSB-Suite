
from algorithms import *

shor = Shor(a=7,N=15)
shor.generate()

grover = Grover(qubits=3)
grover.generate(oracle=3)
grover.generate_kSAT(oracle=[-1,-2,-3,-1,-2,3,-1,2,-3,1,-2,-3,-1,2,3,1,-2,3,1,2,-3], 
                     kSAT=3, 
                     n_answers=1
                  )

vqc = VQC(qubits=3,parametrized_layers=2)
vqc.generate([0.5,0.3,0.2], [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8])
vqc.generate_random()

supremacy = Supremacy()
supremacy.generate_5_1(depth=5)
supremacy.generate_5_4(depth=4)

random_circuit = Random_circuit(4)
random_circuit.generate(n_gates=20,cgate_ratio=0.3,gate_set="u")
random_circuit.generate(n_gates=20,cgate_ratio=0,gate_set="p")