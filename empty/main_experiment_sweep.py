import numpy as np
import random
import copy
import time
import datetime
import os

# --- 1. THE STABLE ENGINE ---
WINDOW_SIZE = 16
NUM_INPUTS = WINDOW_SIZE
COLS = 40
GATE_NAMES = {0: 'AND', 1: 'OR', 2: 'XOR', 3: 'NAND', 4: 'NOR', 5: 'NOT', 6: 'WIRE'}


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


# --- VHDL GENERATOR (Integrated) ---
def generate_vhdl(individual, run_id, penalty, label="CHAMPION"):
    nodes = individual.nodes
    output_node = individual.output_node

    vhdl = []
    vhdl.append(f"-- REFLEX ENGINE GENERATED: {datetime.datetime.now()}")
    vhdl.append(f"-- Run ID: {run_id} | Penalty: {penalty}")
    vhdl.append(f"-- Label: {label}")
    vhdl.append("library IEEE;")
    vhdl.append("use IEEE.STD_LOGIC_1164.ALL;")
    vhdl.append("")
    # Unique Entity Name to avoid conflicts
    entity_name = f"reflex_core_run{run_id}"
    vhdl.append(f"entity {entity_name} is")
    vhdl.append("    Port ( clk : in STD_LOGIC;")
    vhdl.append("           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);")
    vhdl.append("           alarm_out : out STD_LOGIC);")
    vhdl.append(f"end {entity_name};")
    vhdl.append("")
    vhdl.append(f"architecture Behavioral of {entity_name} is")

    num_inputs = 16
    total_wires = num_inputs + len(nodes)

    vhdl.append(f"    signal w : std_logic_vector({total_wires - 1} downto 0);")
    vhdl.append("begin")
    vhdl.append("    w(15 downto 0) <= sensor_stream;")

    for i, node in enumerate(nodes):
        func, in1, in2 = node
        wire_idx = num_inputs + i
        if func == 0:
            line = f"    w({wire_idx}) <= w({in1}) and w({in2});"
        elif func == 1:
            line = f"    w({wire_idx}) <= w({in1}) or w({in2});"
        elif func == 2:
            line = f"    w({wire_idx}) <= w({in1}) xor w({in2});"
        elif func == 3:
            line = f"    w({wire_idx}) <= not(w({in1}) and w({in2}));"
        elif func == 4:
            line = f"    w({wire_idx}) <= not(w({in1}) or w({in2}));"
        elif func == 5:
            line = f"    w({wire_idx}) <= not w({in1});"
        elif func == 6:
            line = f"    w({wire_idx}) <= w({in1});"
        vhdl.append(line)

    vhdl.append(f"    alarm_out <= w({output_node});")
    vhdl.append("end Behavioral;")

    filename = f"reflex_core_run{run_id}.vhd"
    with open(filename, "w") as f:
        f.write("\n".join(vhdl))
    print(f"✅ Auto-Saved VHDL to: {filename}")


def evolve_reflex_static(run_id, normal_data, fault_data, penalty_factor, generations=1000):
    X_normal = create_sliding_windows(normal_data, WINDOW_SIZE)
    X_fault = create_sliding_windows(fault_data, WINDOW_SIZE)
    max_recall_possible = (np.sum(fault_data) / len(fault_data)) * 100.0

    POP_SIZE = 10
    population = [Individual() for _ in range(POP_SIZE)]
    for p in population: p.randomize()

    best_global = None
    best_score = -9999

    start_time = time.time()

    for gen in range(generations):
        # 1. Evaluate
        for ind in population:
            out_normal = ind.evaluate(X_normal)
            out_fault = ind.evaluate(X_fault)

            ind.fpr = np.sum(out_normal) / len(normal_data) * 100.0
            ind.recall = np.sum(out_fault) / len(fault_data) * 100.0

            # Static Fitness
            if ind.fpr > 15.0:
                ind.fitness = -100.0
            else:
                ind.fitness = ind.recall - (penalty_factor * ind.fpr)

            if ind.fitness > best_score:
                best_score = ind.fitness
                best_global = copy.deepcopy(ind)

        # 2. Selection & Mutation
        population = [copy.deepcopy(best_global) for _ in range(POP_SIZE)]
        for i in range(1, POP_SIZE):
            child = population[i]
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

    duration = time.time() - start_time
    efficiency = (best_global.recall / max_recall_possible) * 100.0

    print(
        f"Run {run_id:<2} | Penalty {penalty_factor:<4.1f} | Rec {best_global.recall:.2f}% (Eff: {efficiency:.0f}%) | FPR {best_global.fpr:.2f}% | Time {duration:.1f}s")

    return {
        "id": run_id, "circuit": best_global, "penalty": penalty_factor,
        "recall": best_global.recall, "fpr": best_global.fpr,
        "efficiency": efficiency, "score": best_score
    }


# --- 2. EXPERIMENT RUNNER (PARAMETER SWEEP) ---
RUNS = 10
TARGET_FILE = "processed_data/inner_race_binary.npy"  # <--- Currently set to INNER RACE

# --- THE SWEEP STRATEGY ---
PENALTIES = np.linspace(1.0, 10.0, RUNS)

print(f"📂 Loading data for {TARGET_FILE}...")
try:
    normal_data = np.load("processed_data/normal_binary.npy")[:20000]
    fault_data = np.load(TARGET_FILE)[:20000]
except FileNotFoundError:
    print("❌ Error: Run data_loader.py first!")
    exit()

print(f"🚀 Starting PENALTY SWEEP Experiment ({RUNS} runs)...")
print(f"   Searching for the 'Sweet Spot' between Recall and Noise.")
print("-" * 80)

results = []
for i in range(RUNS):
    p_factor = PENALTIES[i]
    result = evolve_reflex_static(i + 1, normal_data, fault_data, penalty_factor=p_factor, generations=1000)
    results.append(result)

print("-" * 80)
print("📊 ANALYZING SWEEP RESULTS...")

# 1. Filter out broken runs
valid_results = [r for r in results if r['recall'] > 0.1]

champion_to_save = None

if not valid_results:
    print("❌ All runs failed to find a circuit.")
else:
    # 2. Sort by False Alarm Rate
    valid_results.sort(key=lambda x: x['fpr'])

    best_safe = valid_results[0]
    champion_to_save = best_safe  # Default to safest

    print(f"\n🏆 SAFEST CHAMPION (Min Noise)")
    print(f"   Run ID:      {best_safe['id']} (Penalty: {best_safe['penalty']:.1f})")
    print(f"   Recall:      {best_safe['recall']:.2f}%")
    print(f"   False Alarm: {best_safe['fpr']:.2f}%")
    print(f"   Efficiency:  {best_safe['efficiency']:.1f}%")

    # 3. Check for Balanced option
    balanced = [r for r in valid_results if r['recall'] > 20.0 and r['fpr'] < 5.0]
    if balanced:
        best_bal = balanced[0]  # Best FPR among balanced
        print(f"\n⚖️ BALANCED CHAMPION (Best Compromise)")
        print(f"   Run ID:      {best_bal['id']} (Penalty: {best_bal['penalty']:.1f})")
        print(f"   Recall:      {best_bal['recall']:.2f}%")
        print(f"   False Alarm: {best_bal['fpr']:.2f}%")

        # Override Champion to Balanced because it's usually better for Thesis
        champion_to_save = best_bal

    # --- AUTO SAVE LOGIC ---
    if champion_to_save:
        print("\n💾 Auto-Saving Champion Circuit...")
        generate_vhdl(champion_to_save['circuit'],
                      champion_to_save['id'],
                      champion_to_save['penalty'],
                      label="SWEEP_WINNER")