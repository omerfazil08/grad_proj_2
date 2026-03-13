import numpy as np
import random
import copy
import time
import datetime

# --- 1. SPECIALIST CONFIGURATION ---
# 1: Inner Race | 2: Ball | 3: Outer Race
FAULT_CHOICE = 1
BEST_PENALTY = 4.0  # Manually enter the best penalty found in selective sweep

GENERATIONS = 1200
NUM_ISLANDS = 4
MIGRATION_INTERVAL = 300
MIGRATION_RATE = 0.1

FAULT_MAP = {
    1: {"name": "inner_race", "file": "processed_data/inner_race_binary.npy"},
    2: {"name": "ball", "file": "processed_data/ball_binary.npy"},
    3: {"name": "outer_race", "file": "processed_data/outer_race_binary.npy"}
}

TARGET_NAME = FAULT_MAP[FAULT_CHOICE]["name"]
TARGET_FILE = FAULT_MAP[FAULT_CHOICE]["file"]

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
            self.nodes.append(
                [random.randint(0, 6), random.randint(0, max_input_idx - 1), random.randint(0, max_input_idx - 1)])
        self.output_node = random.randint(0, NUM_INPUTS + COLS - 1)

    def evaluate(self, inputs):
        batch_size = inputs.shape[0]
        signals = np.zeros((batch_size, NUM_INPUTS + COLS), dtype=np.int8)
        signals[:, :NUM_INPUTS] = inputs
        for i, node in enumerate(self.nodes):
            f, in1, in2 = node
            idx = NUM_INPUTS + i
            v1, v2 = signals[:, in1], signals[:, in2]
            if f == 0:
                signals[:, idx] = v1 & v2
            elif f == 1:
                signals[:, idx] = v1 | v2
            elif f == 2:
                signals[:, idx] = v1 ^ v2
            elif f == 3:
                signals[:, idx] = ~(v1 & v2) & 1
            elif f == 4:
                signals[:, idx] = ~(v1 | v2) & 1
            elif f == 5:
                signals[:, idx] = (~v1) & 1
            elif f == 6:
                signals[:, idx] = v1
        return signals[:, self.output_node]


def generate_vhdl(individual, fault_type):
    entity_name = f"reflex_core_specialized_{fault_type}"
    vhdl = [
        f"-- SPECIALIZED REFLEX ENGINE: {fault_type.upper()}",
        f"-- PENALTY: {BEST_PENALTY} | GENERATIONS: {GENERATIONS}",
        "library IEEE;", "use IEEE.STD_LOGIC_1164.ALL;", "",
        f"entity {entity_name} is",
        "    Port ( clk : in STD_LOGIC; sensor_stream : in STD_LOGIC_VECTOR(15 downto 0); alarm_out : out STD_LOGIC);",
        f"end {entity_name};", "",
        f"architecture Behavioral of {entity_name} is",
        f"    signal w : std_logic_vector({NUM_INPUTS + COLS - 1} downto 0);",
        "begin", "    w(15 downto 0) <= sensor_stream;"
    ]
    for i, node in enumerate(individual.nodes):
        f, in1, in2 = node
        idx = NUM_INPUTS + i
        ops = ["and", "or", "xor", "nand", "nor", "not", "buffer"]
        if f <= 4:
            vhdl.append(f"    w({idx}) <= w({in1}) {ops[f]} w({in2});")
        elif f == 5:
            vhdl.append(f"    w({idx}) <= not w({in1});")
        else:
            vhdl.append(f"    w({idx}) <= w({in1});")
    vhdl.append(f"    alarm_out <= w({individual.output_node});")
    vhdl.append("end Behavioral;")

    with open(f"{entity_name}.vhd", "w") as f:
        f.write("\n".join(vhdl))
    print(f"\n✅ Specialized VHDL saved: {entity_name}.vhd")


def run_islands():
    print(f"🏝️ STARTING ISOLATED ISLAND EVOLUTION FOR {TARGET_NAME.upper()}")
    print(f"   Using Specialist Penalty: {BEST_PENALTY}")
    print("-" * 80)

    try:
        normal = np.load("processed_data/normal_binary.npy")[:20000]
        fault = np.load(TARGET_FILE)[:20000]
    except FileNotFoundError:
        print("❌ Error: Missing .npy files in processed_data/")
        return

    X_n = np.lib.stride_tricks.as_strided(normal, (normal.size - 15, 16), (normal.itemsize, normal.itemsize))
    X_f = np.lib.stride_tricks.as_strided(fault, (fault.size - 15, 16), (fault.itemsize, fault.itemsize))

    # Initialize Islands
    islands = [[Individual() for _ in range(10)] for _ in range(NUM_ISLANDS)]
    for isl in islands: [ind.randomize() for ind in isl]
    best_per_island = [None] * NUM_ISLANDS

    for gen in range(GENERATIONS):
        island_logs = []
        for i in range(NUM_ISLANDS):
            for ind in islands[i]:
                out_n, out_f = ind.evaluate(X_n), ind.evaluate(X_f)
                ind.fpr, ind.recall = np.mean(out_n) * 100, np.mean(out_f) * 100
                ind.fitness = ind.recall - (BEST_PENALTY * ind.fpr)

            islands[i].sort(key=lambda x: x.fitness, reverse=True)
            best_per_island[i] = copy.deepcopy(islands[i][0])
            island_logs.append(f"Is{i}: R{best_per_island[i].recall:.1f}%/F{best_per_island[i].fpr:.2f}%")

            # Evolution Step (1+9)
            new_pop = [copy.deepcopy(best_per_island[i]) for _ in range(10)]
            for j in range(1, 10):
                for _ in range(random.randint(1, 4)):
                    idx, c = random.randint(0, COLS - 1), random.randint(0, 2)
                    if c == 0:
                        new_pop[j].nodes[idx][0] = random.randint(0, 6)
                    else:
                        new_pop[j].nodes[idx][c] = random.randint(0, NUM_INPUTS + idx - 1)
            islands[i] = new_pop

        # Log Progress every 100 generations
        if gen % 100 == 0:
            print(f"Gen {gen:4d} | {' | '.join(island_logs)}")

        # Secure Migration
        if gen % MIGRATION_INTERVAL == 0 and gen > 0:
            if random.random() < MIGRATION_RATE:
                print(f"   🌊 Secure Migration Event at Generation {gen}...")
                for i in range(NUM_ISLANDS):
                    source, dest = i, (i + 1) % NUM_ISLANDS
                    islands[dest][random.randint(5, 9)] = copy.deepcopy(best_per_island[source])

    final_champion = max(best_per_island, key=lambda x: x.fitness)
    print("-" * 80)
    print(f"🏆 SPECIALIST FOUND FOR {TARGET_NAME.upper()}")
    print(f"   Recall: {final_champion.recall:.2f}% | FPR: {final_champion.fpr:.2f}%")
    generate_vhdl(final_champion, TARGET_NAME)


if __name__ == "__main__":
    run_islands()