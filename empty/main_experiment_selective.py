import numpy as np
import random
import copy
import time
import datetime
import os

# --- 1. USER SELECTION ---
# 1 = Inner Race | 2 = Ball | 3 = Outer Race
FAULT_CHOICE = 3  # <--- CHANGE THIS FOR EACH RUN

FAULT_MAP = {
    1: {"name": "inner_race", "file": "processed_data/inner_race_binary.npy"},
    2: {"name": "ball", "file": "processed_data/ball_binary.npy"},
    3: {"name": "outer_race", "file": "processed_data/outer_race_binary.npy"}
}

TARGET_NAME = FAULT_MAP[FAULT_CHOICE]["name"]
TARGET_FILE = FAULT_MAP[FAULT_CHOICE]["file"]

# --- 2. ENGINE SETTINGS ---
WINDOW_SIZE = 16
NUM_INPUTS = WINDOW_SIZE
COLS = 40


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


def generate_vhdl(individual, fault_type):
    # Unique Entity Name based on fault type
    entity_name = f"reflex_core_{fault_type}"
    vhdl = [
        f"-- REFLEX ENGINE: {fault_type.upper()} FAULT DETECTOR",
        f"-- GENERATED: {datetime.datetime.now()}",
        "library IEEE;", "use IEEE.STD_LOGIC_1164.ALL;", "",
        f"entity {entity_name} is",
        "    Port ( clk : in STD_LOGIC;",
        "           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);",
        "           alarm_out : out STD_LOGIC);",
        f"end {entity_name};", "",
        f"architecture Behavioral of {entity_name} is",
        f"    signal w : std_logic_vector({NUM_INPUTS + COLS - 1} downto 0);",
        "begin", "    w(15 downto 0) <= sensor_stream;"
    ]
    for i, node in enumerate(individual.nodes):
        func, in1, in2 = node
        wire_idx = NUM_INPUTS + i
        if func == 0:
            vhdl.append(f"    w({wire_idx}) <= w({in1}) and w({in2});")
        elif func == 1:
            vhdl.append(f"    w({wire_idx}) <= w({in1}) or w({in2});")
        elif func == 2:
            vhdl.append(f"    w({wire_idx}) <= w({in1}) xor w({in2});")
        elif func == 3:
            vhdl.append(f"    w({wire_idx}) <= not(w({in1}) and w({in2}));")
        elif func == 4:
            vhdl.append(f"    w({wire_idx}) <= not(w({in1}) or w({in2}));")
        elif func == 5:
            vhdl.append(f"    w({wire_idx}) <= not w({in1});")
        elif func == 6:
            vhdl.append(f"    w({wire_idx}) <= w({in1});")
    vhdl.append(f"    alarm_out <= w({individual.output_node});")
    vhdl.append("end Behavioral;")

    filename = f"{entity_name}.vhd"
    with open(filename, "w") as f:
        f.write("\n".join(vhdl))
    print(f"✅ VHDL Saved: {filename}")


def evolve_reflex_static(run_id, normal_data, fault_data, penalty_factor):
    X_normal = create_sliding_windows(normal_data, WINDOW_SIZE)
    X_fault = create_sliding_windows(fault_data, WINDOW_SIZE)
    best_global = None
    best_score = -9999
    population = [Individual() for _ in range(10)]
    for p in population: p.randomize()
    for gen in range(1000):
        for ind in population:
            out_n, out_f = ind.evaluate(X_normal), ind.evaluate(X_fault)
            ind.fpr, ind.recall = np.mean(out_n) * 100, np.mean(out_f) * 100
            ind.fitness = ind.recall - (penalty_factor * ind.fpr)
            if ind.fitness > best_score:
                best_score = ind.fitness
                best_global = copy.deepcopy(ind)
        population = [copy.deepcopy(best_global) for _ in range(10)]
        for i in range(1, 10):
            child = population[i]
            for _ in range(random.randint(1, 5)):
                idx, ctype = random.randint(0, COLS - 1), random.randint(0, 2)
                if ctype == 0:
                    child.nodes[idx][0] = random.randint(0, 6)
                else:
                    child.nodes[idx][ctype] = random.randint(0, NUM_INPUTS + idx - 1)
            if random.random() < 0.2: child.output_node = random.randint(0, NUM_INPUTS + COLS - 1)
    return best_global, best_score, best_global.recall, best_global.fpr


# --- 3. RUNNER ---
print(f"📂 Targeting: {TARGET_NAME.upper()}")
print(f"📂 Loading data from {TARGET_FILE}...")
try:
    normal_data = np.load("processed_data/normal_binary.npy")[:20000]
    fault_data = np.load(TARGET_FILE)[:20000]
except FileNotFoundError:
    print("❌ Error: Run data_loader.py first!")
    exit()

print(f"🚀 Starting PENALTY SWEEP Experiment (3 Settings)...")
print(f"   Searching for the 'Sweet Spot' between Recall and Noise.")
print("-" * 80)

results = []
for p in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0,11.5,12.0,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19.5,20.0]:
    # Running evolution
    ind, score, rec, fpr = evolve_reflex_static(1, normal_data, fault_data, p)

    # Calculate Theoretical Max Recall for Efficiency Metric
    max_recall_possible = (np.sum(fault_data) / len(fault_data)) * 100.0
    efficiency = (rec / max_recall_possible) * 100.0

    print(f"Run | Penalty {p:<4.1f} | Rec {rec:.2f}% (Eff: {efficiency:.0f}%) | FPR {fpr:.2f}%")

    results.append({
        "circuit": ind,
        "penalty": p,
        "recall": rec,
        "fpr": fpr,
        "efficiency": efficiency,
        "score": score
    })

print("-" * 80)
print("📊 ANALYZING SWEEP RESULTS...")

# Sort by FPR (Safest first)
results.sort(key=lambda x: x['fpr'])
best_overall = results[0]  # Default to safest

# Check if there is a 'Balanced' one (FPR < 1.0% and decent Recall)
balanced = [r for r in results if r['fpr'] < 1.0 and r['recall'] > 5.0]
if balanced:
    balanced.sort(key=lambda x: x['recall'], reverse=True)
    best_overall = balanced[0]
    print(f"\n⚖️  BALANCED CHAMPION SELECTED (Best compromise for {TARGET_NAME})")
else:
    print(f"\n🏆 SAFEST CHAMPION SELECTED (Min Noise for {TARGET_NAME})")

print(f"   Recall:      {best_overall['recall']:.2f}%")
print(f"   False Alarm: {best_overall['fpr']:.2f}%")
print(f"   Efficiency:  {best_overall['efficiency']:.1f}%")

generate_vhdl(best_overall['circuit'], TARGET_NAME)