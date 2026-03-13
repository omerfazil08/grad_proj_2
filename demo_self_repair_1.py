import random
import time
import sys
import copy
from collections import defaultdict

# --- IMPORT CORE ENGINE ---
try:
    from evolution_colab_phase12 import (
        ColabConfig, 
        GATES_SET, 
        init_population_hss, 
        select_parent_tournament, 
        crossover, 
        mutate
    )
    # Import the simplifier
    try:
        from simplifier_phase13 import simplify_genome
        HAS_SIMP = True
    except ImportError:
        HAS_SIMP = False
        
except ImportError:
    print("❌ Error: 'evolution_colab_phase12.py' not found.")
    print("Please upload the Phase 12 files to Colab first.")
    sys.exit(1)

# ==============================================================================
# 1. FAULT-TOLERANT EVALUATION ENGINE
# ==============================================================================

def evaluate_network_with_faults(individual, inputs_dict, broken_gates_set=None):
    """
    Simulates the circuit logic. 
    If a gate is in 'broken_gates_set', its output is forced to 0 (Stuck-at-0 fault).
    """
    signals = inputs_dict.copy()
    
    # Create inverted inputs (nA, nB...)
    for k, v in list(inputs_dict.items()):
        if not k.startswith('n'):
            signals[f"n{k}"] = 1 - v

    for gate in individual:
        gate_name = gate["name"]
        out_name = gate["output"]
        
        # --- FAULT INJECTION POINT ---
        if broken_gates_set and gate_name in broken_gates_set:
            signals[out_name] = 0 
            continue
        # -----------------------------

        gate_type = gate["type"]
        gate_func = GATES_SET[gate_type]["func"]
        gate_inputs = gate["inputs"]

        try:
            # Resolve inputs (default to 0 if missing/broken upstream)
            resolved_inputs = [signals.get(src, 0) for src in gate_inputs]
            signals[out_name] = gate_func(*resolved_inputs)
        except Exception:
            signals[out_name] = 0

    return signals

def fitness_faulty(individual, num_outputs, inputs_set, targets_set, broken_gates_set=None):
    """
    Calculates fitness (correct bits) subject to specific hardware faults.
    """
    score = 0
    # Outputs are always the last N gates in Phase 12
    output_gate_names = [gate["output"] for gate in individual[-num_outputs:]]
    
    # Inputs are A0, A1, A2...
    input_labels = [f"A{i}" for i in range(len(inputs_set[0]))]

    for row_idx, row_tuple in enumerate(inputs_set):
        inp_dict = {label: val for label, val in zip(input_labels, row_tuple)}
        
        signals = evaluate_network_with_faults(individual, inp_dict, broken_gates_set)
        
        for out_idx in range(num_outputs):
            target = targets_set[out_idx][row_idx]
            actual = signals.get(output_gate_names[out_idx], 0)
            if actual == target:
                score += 1
                
    return score

# ==============================================================================
# 2. SMART FAULT FINDER & UTILS
# ==============================================================================

def print_circuit_gates(individual):
    print("   ------------------------------------------------")
    print("   gate  | type       | inputs")
    print("   ------------------------------------------------")
    for g in individual:
        print(f"   {g['name']:5} | {g['type']:10} | {', '.join(g['inputs'])}")
    print("   ------------------------------------------------")

def find_critical_gate(individual, num_outputs, inputs, targets):
    """
    Search for a 'Critical Gate' whose failure drastically drops fitness.
    """
    base_score = fitness_faulty(individual, num_outputs, inputs, targets, None)
    candidates = []

    # Skip output gates (breaking them is trivial/boring). Break internal logic.
    testable_gates = individual[:-num_outputs] 
    if not testable_gates: testable_gates = individual 

    for gate in testable_gates:
        g_name = gate["name"]
        broken_score = fitness_faulty(individual, num_outputs, inputs, targets, {g_name})
        
        drop = base_score - broken_score
        if drop > 0:
            candidates.append((drop, g_name))
    
    if not candidates:
        # Robust or lucky circuit. Pick random internal gate.
        return testable_gates[len(testable_gates)//2]["name"]
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

# ==============================================================================
# 3. CUSTOM EVOLUTION LOOP (REPAIR MODE)
# ==============================================================================

def evolve_repair_mode(population, num_inputs, num_outputs, inputs, targets, cfg, broken_set=None):
    max_score = len(inputs) * num_outputs
    
    for gen in range(cfg.generations):
        # 1. Fault-Aware Fitness
        scores = [fitness_faulty(ind, num_outputs, inputs, targets, broken_set) for ind in population]
        
        best_score = max(scores)
        best_idx = scores.index(best_score)
        best_indiv = population[best_idx]

        if gen % cfg.log_every == 0 or best_score == max_score:
            status = "REPAIRING..." if broken_set else "EVOLVING..."
            print(f"   [{status}] Gen {gen:3d} | Fitness: {best_score}/{max_score}")

        if best_score == max_score:
            return best_indiv, True

        # 2. Selection / Breeding
        new_pop = []
        ranked_indices = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
        for i in ranked_indices[:cfg.elitism]:
            new_pop.append(population[i])

        while len(new_pop) < cfg.pop_size:
            p1 = select_parent_tournament(population, scores, cfg)
            p2 = select_parent_tournament(population, scores, cfg)
            c1, c2 = crossover(p1, p2)
            
            # Higher mutation during repair to break local optima
            rate = cfg.base_mut if broken_set is None else (cfg.base_mut * 2.0)
            
            new_pop.append(mutate(c1, num_inputs, rate, cfg))
            if len(new_pop) < cfg.pop_size:
                new_pop.append(mutate(c2, num_inputs, rate, cfg))
        
        population = new_pop

    return best_indiv, False

# ==============================================================================
# 4. MAIN DEMO (FULL ADDER)
# ==============================================================================

def run_self_repair_demo():
    print("\n================================================================")
    print("       🧬 EVOLVABLE HARDWARE: FULL ADDER REPAIR DEMO 🧬")
    print("================================================================\n")

    # --- SETUP: Full Adder (A, B, Cin -> Sum, Cout) ---
    # Inputs: 3 bits (A0, A1, A2)
    inputs = [
        (0,0,0), (0,0,1), (0,1,0), (0,1,1),
        (1,0,0), (1,0,1), (1,1,0), (1,1,1)
    ]
    # Targets:
    # Sum  = A ^ B ^ C
    # Cout = (A&B) | (C&(A^B))
    target_sum  = [0, 1, 1, 0, 1, 0, 0, 1]
    target_cout = [0, 0, 0, 1, 0, 1, 1, 1]
    
    targets = [target_sum, target_cout]
    
    n_in = 3
    n_out = 2
    input_names = ["A", "B", "Cin"]

    cfg = ColabConfig(
        num_gates=16,           # Larger canvas for Full Adder
        pop_size=300,
        generations=250,
        elitism=15,
        tournament_k=5,
        base_mut=0.10,          
        min_mut=0.01,
        p_choose_primitive=0.6,
        log_every=20,
        record_history=False,
        seed=42,
        size_penalty_lambda=0.0,
        parallel=False 
    )

    # ---------------------------------------------------------
    # PHASE 1: HEALTHY EVOLUTION
    # ---------------------------------------------------------
    print(">>> PHASE 1: INITIAL EVOLUTION (HEALTHY HARDWARE)")
    print("   Goal: Evolve a Full Adder (16 bits correct)")
    
    population = init_population_hss(n_in, cfg)
    best_circuit, success = evolve_repair_mode(population, n_in, n_out, inputs, targets, cfg, broken_set=None)

    if not success:
        print("   [!] Failed to evolve initial circuit. Restarting demo...")
        return run_self_repair_demo()

    print(f"   [SUCCESS] Healthy circuit evolved (Fitness {len(inputs)*n_out}/{len(inputs)*n_out}).")
    print("\n   [HEALTHY GATE LIST]")
    print_circuit_gates(best_circuit)

    if HAS_SIMP:
        print("\n   🧠 Healthy Logic (Simplified):")
        out_gates = [best_circuit[-(n_out-i)]["output"] for i in range(n_out)]
        # Outputs are Sum (Index 0) and Cout (Index 1)
        res = simplify_genome(best_circuit, input_names, out_gates)
        for k, v in res.items():
            print(f"   {k}: {v}")

    # ---------------------------------------------------------
    # PHASE 2: INJECT FAULT
    # ---------------------------------------------------------
    print("\n>>> PHASE 2: HARDWARE FAILURE INJECTION")
    time.sleep(1)
    
    # Find the gate that matters most
    victim = find_critical_gate(best_circuit, n_out, inputs, targets)
    broken_set = {victim}
    
    print(f"   [CRITICAL FAILURE] Component '{victim}' has BURNED OUT (Stuck-at-0).")
    
    broken_score = fitness_faulty(best_circuit, n_out, inputs, targets, broken_set)
    print(f"   [DIAGNOSTIC] System Accuracy dropped to: {broken_score}/16")
    
    if broken_score == 16:
        print("   [Info] Circuit is redundant/robust. Breaking another gate...")
        # Force restart if we didn't break it (rare but possible)
        return run_self_repair_demo()

    # ---------------------------------------------------------
    # PHASE 3: SELF-REPAIR
    # ---------------------------------------------------------
    print("\n>>> PHASE 3: SELF-REPAIR SEQUENCE INITIATED")
    print(f"   [Objective] Re-route logic around '{victim}'.")
    time.sleep(1)
    
    cfg.generations = 300 
    repaired_circuit, repair_success = evolve_repair_mode(population, n_in, n_out, inputs, targets, cfg, broken_set=broken_set)

    if repair_success:
        print("\n   ✅ [SYSTEM RESTORED] Self-Repair Complete!")
        
        print("\n   [REPAIRED GATE LIST]")
        print_circuit_gates(repaired_circuit)
        
        if HAS_SIMP:
            print("\n   🧠 Repaired Logic (New Pathway):")
            out_gates = [repaired_circuit[-(n_out-i)]["output"] for i in range(n_out)]
            res = simplify_genome(repaired_circuit, input_names, out_gates)
            for k, v in res.items():
                print(f"   {k}: {v}")
            
        print("\n   [NOTE] Compare the Gate Lists above. The logic has physically changed.")
    else:
        print(f"\n   ❌ [FAILURE] Best recovery: {fitness_faulty(repaired_circuit, n_out, inputs, targets, broken_set)}/16")

if __name__ == "__main__":
    run_self_repair_demo()