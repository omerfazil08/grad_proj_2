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
    # Import the simplifier to visualize the "Brain" changing
    try:
        from simplifier_phase12 import simplify_genome
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
    # 1. Setup input signals
    signals = inputs_dict.copy()
    
    # 2. Create inverted inputs (nA, nB...)
    for k, v in list(inputs_dict.items()):
        if not k.startswith('n'):
            signals[f"n{k}"] = 1 - v

    # 3. Evaluate Gates
    for gate in individual:
        gate_name = gate["name"]
        out_name = gate["output"]
        
        # --- FAULT INJECTION POINT ---
        if broken_gates_set and gate_name in broken_gates_set:
            # The hardware is dead. Output is stuck at 0 (or 1).
            signals[out_name] = 0 
            continue
        # -----------------------------

        gate_type = gate["type"]
        gate_func = GATES_SET[gate_type]["func"]
        gate_inputs = gate["inputs"]

        try:
            # Resolve input values (look up in signals dict)
            # If a previous gate was broken/missing, default to 0
            resolved_inputs = [signals.get(src, 0) for src in gate_inputs]
            
            # Compute logic
            signals[out_name] = gate_func(*resolved_inputs)
            
        except Exception:
            signals[out_name] = 0

    return signals

def fitness_faulty(individual, num_outputs, inputs_set, targets_set, broken_gates_set=None):
    """
    Calculates fitness (correct bits) subject to specific hardware faults.
    """
    score = 0
    output_gate_names = [gate["output"] for gate in individual[-num_outputs:]]
    input_labels = [f"A{i}" for i in range(len(inputs_set[0]))]

    for row_idx, row_tuple in enumerate(inputs_set):
        # Build input dict for this row
        inp_dict = {label: val for label, val in zip(input_labels, row_tuple)}
        
        # Run simulation with faults
        signals = evaluate_network_with_faults(individual, inp_dict, broken_gates_set)
        
        # Check outputs
        for out_idx in range(num_outputs):
            target = targets_set[out_idx][row_idx]
            actual = signals.get(output_gate_names[out_idx], 0)
            if actual == target:
                score += 1
                
    return score

# ==============================================================================
# 2. SMART FAULT FINDER
# ==============================================================================

def find_critical_gate(individual, num_outputs, inputs, targets):
    """
    Instead of breaking a random gate (which might be unused), 
    we search for a 'Critical Gate' whose failure drastically drops fitness.
    """
    base_score = fitness_faulty(individual, num_outputs, inputs, targets, None)
    candidates = []

    # Skip the very last gates if they are direct outputs (too easy to break)
    # We want to break internal logic to force re-routing.
    testable_gates = individual[:-num_outputs] 
    if not testable_gates: testable_gates = individual # Fallback for small nets

    for gate in testable_gates:
        g_name = gate["name"]
        # Test fitness if this gate dies
        broken_score = fitness_faulty(individual, num_outputs, inputs, targets, {g_name})
        
        drop = base_score - broken_score
        if drop > 0:
            candidates.append((drop, g_name))
    
    if not candidates:
        # No single gate failure hurts? Robust (or lucky)! Pick random non-output.
        return testable_gates[len(testable_gates)//2]["name"]
    
    # Return the gate that causes the biggest damage
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

# ==============================================================================
# 3. CUSTOM EVOLUTION LOOP (REPAIR MODE)
# ==============================================================================

def evolve_repair_mode(population, num_inputs, num_outputs, inputs, targets, cfg, broken_set=None):
    """
    Runs the GA loop using the fault-aware fitness function.
    """
    max_score = len(inputs) * num_outputs
    
    for gen in range(cfg.generations):
        # 1. Fitness (Fault Aware)
        scores = [fitness_faulty(ind, num_outputs, inputs, targets, broken_set) for ind in population]
        
        best_score = max(scores)
        best_idx = scores.index(best_score)
        best_indiv = population[best_idx]

        # 2. Log
        if gen % cfg.log_every == 0 or best_score == max_score:
            status = "REPAIRING..." if broken_set else "EVOLVING..."
            print(f"   [{status}] Gen {gen:3d} | Fitness: {best_score}/{max_score}")

        if best_score == max_score:
            return best_indiv, True

        # 3. Selection / Breeding
        new_pop = []
        
        # Elitism
        ranked_indices = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
        for i in ranked_indices[:cfg.elitism]:
            new_pop.append(population[i])

        while len(new_pop) < cfg.pop_size:
            p1 = select_parent_tournament(population, scores, cfg)
            p2 = select_parent_tournament(population, scores, cfg)
            c1, c2 = crossover(p1, p2)
            
            # Adaptive mutation for repair:
            # If repairing, use slightly higher mutation to break out of the "broken" structure
            rate = cfg.base_mut if broken_set is None else (cfg.base_mut * 1.5)
            
            new_pop.append(mutate(c1, num_inputs, rate, cfg))
            if len(new_pop) < cfg.pop_size:
                new_pop.append(mutate(c2, num_inputs, rate, cfg))
        
        population = new_pop

    return best_indiv, False

# ==============================================================================
# 4. MAIN DEMO
# ==============================================================================

def run_self_repair_demo():
    print("\n================================================================")
    print("       🧬 EVOLVABLE HARDWARE: SELF-REPAIR DEMONSTRATION 🧬")
    print("================================================================\n")

    # --- SETUP: 3-Input Majority Voter ---
    # Output 1 if two or more inputs are 1.
    inputs = [
        (0,0,0), (0,0,1), (0,1,0), (0,1,1),
        (1,0,0), (1,0,1), (1,1,0), (1,1,1)
    ]
    targets = [[0, 0, 0, 1, 0, 1, 1, 1]]
    
    n_in = 3
    n_out = 1
    input_names = ["A0", "A1", "A2"]

    cfg = ColabConfig(
        num_gates=12,           # Enough redundancy to allow repair
        pop_size=300,
        generations=200,
        elitism=10,
        tournament_k=5,
        base_mut=0.15,          # High mutation for small circuits
        min_mut=0.01,
        p_choose_primitive=0.6,
        log_every=20,
        record_history=False,
        seed=42,
        size_penalty_lambda=0.0,
        parallel=False          # Use Serial for this specific demo logic
    )

    # ---------------------------------------------------------
    # PHASE 1: HEALTHY EVOLUTION
    # ---------------------------------------------------------
    print(">>> PHASE 1: INITIAL EVOLUTION (HEALTHY HARDWARE)")
    population = init_population_hss(n_in, cfg)
    best_circuit, success = evolve_repair_mode(population, n_in, n_out, inputs, targets, cfg, broken_set=None)

    if not success:
        print("   [!] Failed to evolve initial circuit. Restarting demo...")
        return run_self_repair_demo()

    print("   [SUCCESS] Healthy circuit evolved (Fitness 8/8).")
    
    if HAS_SIMP:
        print("\n   🧠 Healthy Logic:")
        out_gate = best_circuit[-1]["output"]
        res = simplify_genome(best_circuit, input_names, [out_gate])
        print(f"   {res[list(res.keys())[0]]}")

    # ---------------------------------------------------------
    # PHASE 2: INJECT FAULT
    # ---------------------------------------------------------
    print("\n>>> PHASE 2: HARDWARE FAILURE INJECTION")
    time.sleep(1)
    
    # Find the gate that matters most
    victim = find_critical_gate(best_circuit, n_out, inputs, targets)
    broken_set = {victim}
    
    print(f"   [CRITICAL FAILURE] Gate '{victim}' has BURNED OUT (Stuck-at-0).")
    
    # Verify it's broken
    broken_score = fitness_faulty(best_circuit, n_out, inputs, targets, broken_set)
    print(f"   [DIAGNOSTIC] System Accuracy dropped to: {broken_score}/8")
    
    if broken_score == 8:
        print("   [Wait...] The system is naturally robust! It still works.")
        print("   (This is rare but possible with redundancy. Restarting to force a break.)")
        return run_self_repair_demo()

    # ---------------------------------------------------------
    # PHASE 3: SELF-REPAIR
    # ---------------------------------------------------------
    print("\n>>> PHASE 3: SELF-REPAIR SEQUENCE INITIATED")
    print("   [Objective] Re-route logic to bypass the dead gate.")
    time.sleep(1)

    # Important: We keep the *current* population (which contains the broken best_circuit)
    # This simulates the hardware attempting to heal itself in real-time.
    
    cfg.generations = 300 # Give it time to fix
    repaired_circuit, repair_success = evolve_repair_mode(population, n_in, n_out, inputs, targets, cfg, broken_set=broken_set)

    if repair_success:
        print("\n   ✅ [SYSTEM RESTORED] Self-Repair Complete!")
        print(f"   [Status] Logic successfully re-routed around '{victim}'.")
        
        if HAS_SIMP:
            print("\n   🧠 Repaired Logic (New Pathway):")
            out_gate = repaired_circuit[-1]["output"]
            res = simplify_genome(repaired_circuit, input_names, [out_gate])
            print(f"   {res[list(res.keys())[0]]}")
            
        print("\n   [NOTE] Notice how the logic equation changed/expanded to compensate for the loss.")
    else:
        print("\n   ❌ [FAILURE] Could not fully repair. Best recovery: ", fitness_faulty(repaired_circuit, n_out, inputs, targets, broken_set))

if __name__ == "__main__":
    run_self_repair_demo()