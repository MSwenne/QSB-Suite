
from algorithms import *

adder = Adder(qubits_a=5, qubits_b=5)
grover = Grover(qubits=8)
grover_KSAT = Grover(qubits=7)
palindrome = Palindrome(qubits=10)
random_circuit = Random_circuit(qubits=20)
shor = Shor(a=7,N=15)
supremacy = Supremacy()
vqc = VQC(qubits=5,entanglement_layers=2,parametrized_layers=2)


adder.generate(a=3,b=3)
grover.generate(oracle=42)
grover_KSAT.generate_kSAT(oracle=[   1, 2, 3,
                                     1, 2,-3,
                                     1,-2, 3,
                                    -1, 2, 3,
                                     1,-2,-3,
                                    -1, 2,-3,
                                    -1,-2, 3,
                                    -1,-2, 4,
                                    -1,-2, 5,
                                    -1,-2, 6,
                                    -1,-2, 7
                                ], 
                     kSAT=3, 
                     n_answers=1
                  )
palindrome.generate(n_palindromes=5,n_gates=20,cgate_ratio=0.3, gate_set="u")
random_circuit.generate(n_gates=100,cgate_ratio=0.3,gate_set="u")
shor.generate()
supremacy.generate_5_4(depth=8)
vqc.generate(   datapoint=[0.5,0.4,0.3,0.2,0.1], 
                theta=[ 0.1,0.2,0.3,0.4,0.5,
                        0.6,0.7,0.8,0.9,1.0,
                        1.1,1.2,1.3,1.4,1.5,
                        1.6,1.7,1.8,1.9,2.0,
                        2.1,2.2,2.3,2.4,2.5,
                        2.6,2.7,2.8,2.9,3.0]
            )
# vqc.generate_random(seed=42)




