import numpy as np
import random
import copy
import time

# --- 1. THE HEAVY DUTY ENGINE ---
# We increased Population and Generations because you said run-time is not a concern.
WINDOW_SIZE = 16
NUM_INPUTS = WINDOW_SIZE
COLS = 40  # Increased columns slightly for more complex potential logic
GATE_NAMES = {0: 'AND', 1: 'OR', 2: 'XOR', 3: 'NAND', 4: 'NOR', 5: 'NOT', 6: 'WIRE'}

# --- ADAPTIVE SETTINGS ---
TARGET_FPR = 1.0  # We want the noise to be EXACTLY around 1% (or less)
PENALTY_LEARNING_RATE = 0.05  # How fast the penalty reacts (5% change per gen)


class Individual:
    def __init__(self):
        self.nodes = []
        self.output_node = 0
        self.fitness = -9999.0
        self.recall = 0.0
        self.fpr = 0.0

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
        # Optimized Numpy Vectorization
        batch_size = inputs.shape[0]
        signals = np.zeros((batch_size, NUM_INPUTS + COLS), dtype=np.int8)
        signals[:, :NUM_INPUTS] = inputs
        for i, node in enumerate(self.nodes):
            func, in1_idx, in2_idx = node
            idx_in_signals = NUM_INPUTS + i
            val1 = signals[:, in1_idx]
            val2 = signals[:, in2_idx]

            if func == 0:
                signals[:, idx_in_signals] = val1 & val2
            elif func == 1:
                signals[:, idx_in_signals] = val1 | val2
            elif func == 2:
                signals[:, idx_in_signals] = val1 ^ val2
            elif func == 3:
                signals[:, idx_in_signals] = ~(val1 & val2) & 1
            elif func == 4:
                signals[:, idx_in_signals] = ~(val1 | val2) & 1
            elif func == 5:
                signals[:, idx_in_signals] = (~val1) & 1
            elif func == 6:
                signals[:, idx_in_signals] = val1

        return signals[:, self.output_node]


def create_sliding_windows(data, window_size):
    shape = (data.size - window_size + 1, window_size)
    strides = (data.itemsize, data.itemsize)
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)


def evolve_reflex_adaptive(run_id, normal_data, fault_data, generations=1000):
    """
    The Adaptive Evolution Engine.
    Adjusts penalty DYNAMICALLY during the run.
    """
    X_normal = create_sliding_windows(normal_data, WINDOW_SIZE)
    X_fault = create_sliding_windows(fault_data, WINDOW_SIZE)
    max_recall_possible = (np.sum(fault_data) / len(fault_data)) * 100.0

    # Larger Population for better search
    POP_SIZE = 10
    population = [Individual() for _ in range(POP_SIZE)]
    for p in population: p.randomize()

    best_global = None
    best_score = -9999

    # Start with a neutral penalty
    current_penalty = 2.0

    start_time = time.time()

    for gen in range(generations):
        # 1. Evaluate Population
        gen_best_fpr = 100.0

        for ind in population:
            out_normal = ind.evaluate(X_normal)
            out_fault = ind.evaluate(X_fault)

            ind.fpr = np.sum(out_normal) / len(normal_data) * 100.0
            ind.recall = np.sum(out_fault) / len(fault_data) * 100.0

            # --- THE ADAPTIVE FITNESS FUNCTION ---
            # Fitness = Recall - (Variable_Penalty * FPR)
            ind.fitness = ind.recall - (current_penalty * ind.fpr)

            # Track Global Best
            if ind.fitness > best_score:
                best_score = ind.fitness
                best_global = copy.deepcopy(ind)

            if ind.fpr < gen_best_fpr:
                gen_best_fpr = ind.fpr

        # 2. ADAPT THE PENALTY (The Thermostat)
        # If the best circuit in this generation is too noisy -> Increase Penalty
        # If the best circuit is too quiet (too safe) -> Decrease Penalty
        if gen_best_fpr > TARGET_FPR:
            current_penalty *= (1.0 + PENALTY_LEARNING_RATE)
        elif gen_best_fpr < (TARGET_FPR * 0.5):  # If FPR is super low (<0.5%)
            current_penalty *= (1.0 - PENALTY_LEARNING_RATE)

        # Clamp penalty to sane values to prevent explosion
        current_penalty = max(0.1, min(current_penalty, 50.0))

        # 3. Selection & Mutation (1+9 Strategy now)
        population = [copy.deepcopy(best_global) for _ in range(POP_SIZE)]
        for i in range(1, POP_SIZE):
            child = population[i]
            # Heavier Mutation: 1 to 5 gene changes allowed
            for _ in range(random.randint(1, 5)):
                node_idx = random.randint(0, COLS - 1)
                change_type = random.randint(0, 2)
                if change_type == 0:
                    child.nodes[node_idx][0] = random.randint(0, 6)
                elif change_type == 1:
                    child.nodes[node_idx][1] = random.randint(0, NUM_INPUTS + node_idx - 1)
                elif change_type == 2:
                    child.nodes[node_idx][2] = random.randint(0, NUM_INPUTS + node_idx - 1)
            if random.random() < 0.2: child.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

    # Final Stats
    duration = time.time() - start_time
    efficiency = (best_global.recall / max_recall_possible) * 100.0

    print(
        f"Run {run_id}: Rec {best_global.recall:.2f}% (Eff: {efficiency:.0f}%) | FPR {best_global.fpr:.2f}% | Final Penalty {current_penalty:.1f} | Time {duration:.1f}s")

    return {
        "id": run_id, "circuit": best_global,
        "recall": best_global.recall, "fpr": best_global.fpr,
        "efficiency": efficiency, "score": best_score
    }


# --- 2. EXPERIMENT RUNNER ---
RUNS = 10
# Note: Generaions moved inside the function default (1000)
TARGET_FILE = "processed_data/outer_race_binary.npy"  # <--- START WITH OUTER (Loudest) or BALL (Hardest)

print(f"📂 Loading data...")
try:
    normal_data = np.load("processed_data/normal_binary.npy")[:20000]
    fault_data = np.load(TARGET_FILE)[:20000]
except FileNotFoundError:
    print("❌ Error: Run data_loader.py first!")
    exit()

print(f"🚀 Starting HEAVY DUTY Adaptive Experiment ({RUNS} runs x 1000 Gens)...")
print(f"   Target FPR: {TARGET_FPR}%")
print("-" * 75)

results = []
for i in range(RUNS):
    result = evolve_reflex_adaptive(i + 1, normal_data, fault_data, generations=1000)
    results.append(result)

print("-" * 75)
print("📊 ANALYZING CHAMPIONS...")

# Filter for strictly safe candidates first
safe_candidates = [r for r in results if r['fpr'] <= (TARGET_FPR * 1.5)]  # Allow tiny margin

champion = None
if safe_candidates:
    print(f"✅ Found {len(safe_candidates)} SAFE candidates (FPR near {TARGET_FPR}%).")
    safe_candidates.sort(key=lambda x: x['recall'], reverse=True)
    champion = safe_candidates[0]
else:
    print("⚠️ No strictly safe candidates. The signal might be too noisy.")
    results.sort(key=lambda x: x['score'], reverse=True)
    champion = results[0]

print(f"\n🏆 ULTIMATE ADAPTIVE CHAMPION (Run {champion['id']})")
print(f"   Recall:      {champion['recall']:.4f}%")
print(f"   Efficiency:  {champion['efficiency']:.2f}%")
print(f"   False Alarm: {champion['fpr']:.4f}%")

best_global = champion['circuit']
# If you want VHDL immediately:
# import vhdl_exporter
# vhdl_exporter.generate_vhdl(best_global, champion['id'], 0.0)