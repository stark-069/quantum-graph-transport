import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from IPython.display import display

def build_labeled_circuit():
    # --- CHANGE: Explicitly name the registers ---
    q_data = QuantumRegister(3, 'data')    # Top 3 wires (q0, q1, q2)
    q_anc  = QuantumRegister(1, 'ancilla') # Bottom wire (q3)
    c_reg  = ClassicalRegister(4, 'c')
    
    # Create circuit with distinct registers
    qc = QuantumCircuit(q_data, q_anc, c_reg)

    # Note: q_anc[0] acts as index 3 in the previous logic
    # q_data[0] is q0, q_data[1] is q1, q_data[2] is q2

    # 1. Split (Node 1 -> 2 & 6)
    qc.h(q_data[2])
    qc.x(q_data[0])
    qc.cx(q_data[2], q_data[0])
    qc.barrier()

    # 2. Propagate
    qc.ch(q_data[2], q_data[1])
    qc.cx(q_data[2], q_data[0])
    qc.x(q_data[2])
    qc.ccx(q_data[2], q_data[0], q_data[1])
    qc.x(q_data[2])
    qc.barrier()

    # 3. Merge
    qc.ccx(q_data[2], q_data[1], q_data[0])
    qc.ccx(q_data[2], q_data[0], q_data[1])
    qc.barrier()

    # 4. Transport to Ancilla
    # We target q_anc[0] now
    qc.mcx([q_data[0], q_data[1], q_data[2]], q_anc[0]) 
    qc.x(q_data[2])
    qc.mcx([q_data[0], q_data[1], q_data[2]], q_anc[0])
    qc.x(q_data[2])
    qc.barrier()

    # 5. Reset Data
    qc.cx(q_anc[0], q_data[0])
    qc.cx(q_anc[0], q_data[1])

    qc.measure(q_data, c_reg[0:3]) # Measure data to first 3 bits
    qc.measure(q_anc, c_reg[3])    # Measure ancilla to 4th bit
    return qc

# --- Run & Display ---
qc_labeled = build_labeled_circuit()

print("Labeled Circuit Diagram (Look at the bottom wire!):")
display(qc_labeled.draw(output='mpl', style='iqp'))

# Run Simulation
sim = AerSimulator()
t_qc = transpile(qc_labeled, sim)
res = sim.run(t_qc).result()
display(plot_histogram(res.get_counts()))

qc_labeled.draw(output='mpl', style='iqp').savefig('circuit_diagram.png')
plot_histogram(res.get_counts()).savefig('histogram.png')