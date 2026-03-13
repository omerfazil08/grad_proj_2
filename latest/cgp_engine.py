# cgp_engine.py
import numpy as np
import random
import copy

# --- HARDWARE CONSTANTS ---
WINDOW_SIZE = 16
NUM_INPUTS = WINDOW_SIZE
COLS = 30
GATE_NAMES = {0: 'AND', 1: 'OR', 2: 'XOR', 3: 'NAND', 4: 'NOR', 5: 'NOT', 6: 'WIRE'}

class Individual:
    def __init__(self):
        self.nodes = []
        self.output_node = 0
        self.fitness = -100.0

    def randomize(self):
        self.nodes = []
        for i in range(COLS):
            max_input_idx = NUM_INPUTS + i
            func = random.randint(0, 6)
            in1 = random.randint(0, max_input_idx - 1)
            in2 = random.randint(0, max_input_idx - 1)
            self.nodes.append([func, in1, in2])
        self.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

    def evaluate(self, inputs):
        batch_size = inputs.shape[0]
        signals = np.zeros((batch_size, NUM_INPUTS + COLS), dtype=np.int8)
        signals[:, :NUM_INPUTS] = inputs
        for i, node in enumerate(self.nodes):
            func, in1_idx, in2_idx = node
            idx_in_signals = NUM_INPUTS + i
            val1 = signals[:, in1_idx]
            val2 = signals[:, in2_idx]
            
            if func == 0: signals[:, idx_in_signals] = val1 & val2
            elif func == 1: signals[:, idx_in_signals] = val1 | val2
            elif func == 2: signals[:, idx_in_signals] = val1 ^ val2
            elif func == 3: signals[:, idx_in_signals] = ~(val1 & val2) & 1
            elif func == 4: signals[:, idx_in_signals] = ~(val1 | val2) & 1
            elif func == 5: signals[:, idx_in_signals] = (~val1) & 1
            elif func == 6: signals[:, idx_in_signals] = val1
            
        return signals[:, self.output_node]

def create_sliding_windows(data, window_size):
    shape = (data.size - window_size + 1, window_size)
    strides = (data.itemsize, data.itemsize)
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

# --- THE EVOLUTION FUNCTION ---
def evolve_reflex(run_id, normal_data, fault_data, generations=200, penalty_factor=0.5):
    """
    Runs one full evolution session.
    Returns the best individual and its stats.
    """
    # 1. Prepare Data
    X_normal = create_sliding_windows(normal_data, WINDOW_SIZE)
    X_fault = create_sliding_windows(fault_data, WINDOW_SIZE)
    
    # Calculate Theoretical Max Recall for Efficiency Metric
    max_recall_possible = (np.sum(fault_data) / len(fault_data)) * 100.0

    # 2. Initialize Population
    population = [Individual() for _ in range(5)] # Small pop (1+4 ES)
    for p in population: p.randomize()

    best_global = None
    best_score = -9999
    
    # 3. Evolution Loop
    for gen in range(generations):
        # Evaluate
        for ind in population:
            out_normal = ind.evaluate(X_normal)
            out_fault = ind.evaluate(X_fault)
            
            fpr = np.sum(out_normal) / len(normal_data) * 100.0
            recall = np.sum(out_fault) / len(fault_data) * 100.0
            
            # FITNESS LOGIC
            if fpr > 10.0:
                ind.fitness = -100.0 # Kill switch for noise
            else:
                ind.fitness = recall - (penalty_factor * fpr)
            
            if ind.fitness > best_score:
                best_score = ind.fitness
                best_global = copy.deepcopy(ind)

        # Selection & Mutation (1+4)
        population = [copy.deepcopy(best_global) for _ in range(5)]
        for i in range(1, 5): # Mutate children
            child = population[i]
            # Mutate 1-3 genes
            for _ in range(random.randint(1, 3)):
                node_idx = random.randint(0, COLS - 1)
                change_type = random.randint(0, 2)
                if change_type == 0: child.nodes[node_idx][0] = random.randint(0, 6)
                elif change_type == 1: child.nodes[node_idx][1] = random.randint(0, NUM_INPUTS + node_idx - 1)
                elif change_type == 2: child.nodes[node_idx][2] = random.randint(0, NUM_INPUTS + node_idx - 1)
            if random.random() < 0.1: child.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

    # 4. Final Stats
    out_fault = best_global.evaluate(X_fault)
    out_normal = best_global.evaluate(X_normal)
    
    final_recall = np.sum(out_fault) / len(fault_data) * 100.0
    final_fpr = np.sum(out_normal) / len(normal_data) * 100.0
    capture_efficiency = (final_recall / max_recall_possible) * 100.0
    
    print(f"Run {run_id}: Recall {final_recall:.2f}% (Eff: {capture_efficiency:.1f}%) | FPR {final_fpr:.2f}% | Score {best_score:.2f}")
    
    return {
        "id": run_id,
        "circuit": best_global,
        "recall": final_recall,
        "fpr": final_fpr,
        "efficiency": capture_efficiency,
        "score": best_score
    }