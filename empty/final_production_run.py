import numpy as np
import random
import copy
import time
import datetime
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
TARGET_FILE = "processed_data/outer_race_binary.npy"  # The Loudest Fault
PENALTY_FACTOR = 10.0  # The Magic Number found in the sweep
GENERATIONS = 1000  # Deep evolution
RUNS = 5  # Give it 5 tries to find a perfect one

# --- ENGINE ---
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


# --- VHDL GENERATOR ---
def generate_vhdl(individual, run_id):
    nodes = individual.nodes
    output_node = individual.output_node

    vhdl = []
    vhdl.append(f"-- REFLEX ENGINE GENERATED: {datetime.datetime.now()}")
    vhdl.append(f"-- Run ID: {run_id} | Penalty: {PENALTY_FACTOR}")
    vhdl.append("library IEEE;")
    vhdl.append("use IEEE.STD_LOGIC_1164.ALL;")
    vhdl.append("")
    vhdl.append(f"entity reflex_core_{run_id} is")
    vhdl.append("    Port ( clk : in STD_LOGIC;")
    vhdl.append("           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);")
    vhdl.append("           alarm_out : out STD_LOGIC);")
    vhdl.append(f"end reflex_core_{run_id};")
    vhdl.append("")
    vhdl.append(f"architecture Behavioral of reflex_core_{run_id} is")

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

    filename = f"reflex_core_final.vhd"
    with open(filename, "w") as f:
        f.write("\n".join(vhdl))
    print(f"✅ VHDL Saved to: {filename}")


# --- MAIN RUNNER ---
def run_final_evolution():
    print(f"📂 Loading data...")
    normal_data = np.load("processed_data/normal_binary.npy")[:20000]
    fault_data = np.load(TARGET_FILE)[:20000]

    X_normal = create_sliding_windows(normal_data, WINDOW_SIZE)
    X_fault = create_sliding_windows(fault_data, WINDOW_SIZE)

    best_run_global = None
    best_score_global = -9999

    print(f"🚀 STARTING PRODUCTION RUN (Penalty={PENALTY_FACTOR})...")

    for run in range(RUNS):
        POP_SIZE = 10
        population = [Individual() for _ in range(POP_SIZE)]
        for p in population: p.randomize()

        best_ind = None
        best_ind_score = -9999

        for gen in range(GENERATIONS):
            for ind in population:
                out_normal = ind.evaluate(X_normal)
                out_fault = ind.evaluate(X_fault)
                ind.fpr = np.sum(out_normal) / len(normal_data) * 100.0
                ind.recall = np.sum(out_fault) / len(fault_data) * 100.0

                # Strict Penalty Logic
                if ind.fpr > 5.0:
                    ind.fitness = -100.0
                else:
                    ind.fitness = ind.recall - (PENALTY_FACTOR * ind.fpr)

                if ind.fitness > best_ind_score:
                    best_ind_score = ind.fitness
                    best_ind = copy.deepcopy(ind)

            # Evolution Step
            population = [copy.deepcopy(best_ind) for _ in range(POP_SIZE)]
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

        print(f"Run {run + 1}: Recall {best_ind.recall:.2f}% | FPR {best_ind.fpr:.2f}%")

        if best_ind.fitness > best_score_global:
            best_score_global = best_ind.fitness
            best_run_global = best_ind

    print("-" * 50)
    print(f"🏆 FINAL CHAMPION SELECTED")
    print(f"   Recall: {best_run_global.recall:.2f}%")
    print(f"   FPR:    {best_run_global.fpr:.2f}%")

    # 1. Generate VHDL
    generate_vhdl(best_run_global, "FINAL")

    # 2. Visualize Logic
    print("📊 Generating Logic Visualization...")
    out_fault = best_run_global.evaluate(X_fault)
    out_normal = best_run_global.evaluate(X_normal)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title(f"Normal Operation (FPR: {best_run_global.fpr:.2f}%)")
    plt.plot(normal_data[:1000], 'g', alpha=0.3, label="Input Noise")
    plt.fill_between(range(1000), 0, 1, where=(out_normal[:1000] == 1), color='red', alpha=0.9, label="False Alarm")
    plt.legend(loc='upper right')

    plt.subplot(2, 1, 2)
    plt.title(f"Fault Operation (Recall: {best_run_global.recall:.2f}%)")
    plt.plot(fault_data[:1000], 'k', alpha=0.3, label="Fault Input")
    plt.fill_between(range(1000), 0, 1, where=(out_fault[:1000] == 1), color='red', alpha=0.9, label="Reflex Trigger")
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig("final_logic_performance.png")
    print("📸 Saved plot to 'final_logic_performance.png'")


if __name__ == "__main__":
    run_final_evolution()