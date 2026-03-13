import numpy as np
import random
import copy
import time

# --- CONFIGURATION (The "Hardware Contract") ---
WINDOW_SIZE = 16       # The "Reflex" sees the last 16 bits (Shift Register)
NUM_INPUTS = WINDOW_SIZE
NUM_OUTPUTS = 1
ROWS = 1               # CGP Geometry (1 Row = Linear Chain)
COLS = 30              # Max 30 gates available

LEVELS_BACK = 30       # Feed-forward constraint (can connect to any previous node)

# Load the binary data
print("⏳ Loading data...")
normal_data = np.load("processed_data/normal_binary.npy")
fault_data = np.load("processed_data/inner_race_binary.npy") # Starting with the "Easy" fault

# Training Split (Use first 50% for evolution to save time & prevent overfitting)
TRAIN_LIMIT = 20000 
normal_train = normal_data[:TRAIN_LIMIT]
fault_train = fault_data[:TRAIN_LIMIT]

# --- 1. THE VIRTUAL FPGA COMPONENTS ---
# We represent gates as simple integers for speed
# 0: AND, 1: OR, 2: XOR, 3: NAND, 4: NOR, 5: NOT, 6: WIRE (Pass-through)
GATE_NAMES = {0: 'AND', 1: 'OR', 2: 'XOR', 3: 'NAND', 4: 'NOR', 5: 'NOT', 6: 'WIRE'}

def run_gate(op_code, in1, in2):
    """Simulates a single logic gate."""
    if op_code == 0: return in1 & in2       # AND
    if op_code == 1: return in1 | in2       # OR
    if op_code == 2: return in1 ^ in2       # XOR
    if op_code == 3: return ~(in1 & in2) & 1 # NAND
    if op_code == 4: return ~(in1 | in2) & 1 # NOR
    if op_code == 5: return (~in1) & 1      # NOT (ignores in2)
    if op_code == 6: return in1             # WIRE (ignores in2)
    return 0

# --- 2. THE GENOME (The Circuit Blueprint) ---
class Individual:
    def __init__(self):
        # A list of nodes. Each node is [Function, Input1_Index, Input2_Index]
        self.nodes = []
        self.output_node = 0
        self.fitness = 0.0
        self.active_nodes = [] # To count gate usage

    def randomize(self):
        self.nodes = []
        for i in range(COLS):
            # Input indices: 0 to NUM_INPUTS-1 are raw inputs
            # Indices NUM_INPUTS to NUM_INPUTS+i-1 are previous gate outputs
            max_input_idx = NUM_INPUTS + i 
            
            func = random.randint(0, 6)
            in1 = random.randint(0, max_input_idx - 1)
            in2 = random.randint(0, max_input_idx - 1)
            self.nodes.append([func, in1, in2])
        
        # Connect output to one of the last few gates or inputs
        self.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

    def evaluate(self, inputs):
        """
        Runs the circuit on a whole batch of inputs (Vectorized for speed).
        inputs shape: (Batch_Size, WINDOW_SIZE)
        """
        # Node outputs array: [Input0, Input1..., Node0, Node1...]
        batch_size = inputs.shape[0]
        # Pre-allocate memory for all signals (inputs + gate outputs)
        signals = np.zeros((batch_size, NUM_INPUTS + COLS), dtype=np.int8)
        signals[:, :NUM_INPUTS] = inputs

        # Execute gates in feed-forward order
        for i, node in enumerate(self.nodes):
            func, in1_idx, in2_idx = node
            idx_in_signals = NUM_INPUTS + i
            
            val1 = signals[:, in1_idx]
            val2 = signals[:, in2_idx]
            signals[:, idx_in_signals] = run_gate(func, val1, val2)

        return signals[:, self.output_node]

# --- 3. THE EVOLUTION LOOP ---
def create_sliding_windows(data, window_size):
    """Converts 1D stream into 2D sliding windows [N, window_size]"""
    shape = (data.size - window_size + 1, window_size)
    strides = (data.itemsize, data.itemsize)
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

print("⚙️  Preparing sliding windows...")
X_normal = create_sliding_windows(normal_train, WINDOW_SIZE)
X_fault = create_sliding_windows(fault_train, WINDOW_SIZE)

def calculate_fitness(ind):
    # Run circuit on Normal Data
    out_normal = ind.evaluate(X_normal)
    false_positives = np.sum(out_normal) # We want this to be 0
    
    # Run circuit on Fault Data
    out_fault = ind.evaluate(X_fault)
    true_positives = np.sum(out_fault)   # We want this to be high
    
    # Metrics
    recall = true_positives / len(fault_train) * 100.0
    fpr = false_positives / len(normal_train) * 100.0
    
    # FITNESS FUNCTION (The Thesis Logic)
    # We prioritize Low False Alarms (Safety) heavily
    # Score = Recall - (Penalty * FPR)
    score = recall - (3.0 * fpr) 
    
    return score, recall, fpr

# Parameters
POPULATION_SIZE = 5
GENERATIONS = 500
MUTATION_RATE = 0.05

print(f"🚀 Starting Evolution (Target: Inner Race Fault)...")
population = [Individual() for _ in range(POPULATION_SIZE)]
for p in population: p.randomize()

best_global = None
best_score = -9999

try:
    for gen in range(GENERATIONS):
        # 1. Evaluate
        for ind in population:
            ind.fitness, recall, fpr = calculate_fitness(ind)
            
            if ind.fitness > best_score:
                best_score = ind.fitness
                best_global = copy.deepcopy(ind)
                print(f"Gen {gen}: New Best! Recall: {recall:.2f}% | FPR: {fpr:.2f}% | Score: {best_score:.2f}")

        # 2. Select (1+4 Evolutionary Strategy)
        # We keep the single best parent and mutate it to create children
        parent = best_global
        population = [copy.deepcopy(parent) for _ in range(POPULATION_SIZE)]
        
        # 3. Mutate (Skip the first one to keep the elite)
        for i in range(1, POPULATION_SIZE):
            child = population[i]
            # Mutate a few nodes
            for _ in range(random.randint(1, 3)):
                node_idx = random.randint(0, COLS - 1)
                change_type = random.randint(0, 2)
                if change_type == 0: child.nodes[node_idx][0] = random.randint(0, 6) # Change Function
                elif change_type == 1: child.nodes[node_idx][1] = random.randint(0, NUM_INPUTS + node_idx - 1) # Change Input 1
                elif change_type == 2: child.nodes[node_idx][2] = random.randint(0, NUM_INPUTS + node_idx - 1) # Change Input 2
            
            # Occasionally change output node
            if random.random() < 0.1:
                child.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

except KeyboardInterrupt:
    print("\n🛑 Evolution stopped by user.")

print("\n🏆 Evolution Finished.")
if best_global:
    score, recall, fpr = calculate_fitness(best_global)
    print(f"Final Best Circuit -> Recall: {recall:.2f}% | FPR: {fpr:.2f}%")
    print(f"Output Node: {best_global.output_node}")
    print("Logic Gates (Raw Genome):")
    for i, n in enumerate(best_global.nodes):
        print(f"  Node {NUM_INPUTS+i}: {GATE_NAMES[n[0]]}({n[1]}, {n[2]})")