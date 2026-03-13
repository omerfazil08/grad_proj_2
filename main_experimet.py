import numpy as np
import cgp_engine # Import your new module

# --- CONFIGURATION ---
RUNS = 10                  # How many times to try?
GENERATIONS = 300          # How long each run lasts
PENALTY = 1.5              # Safety factor (Higher = Safer, Lower = More Sensitive)
TARGET_FILE = "processed_data/ball_binary.npy" # Change this for different faults!

# Load Data ONCE (to save time)
print(f"📂 Loading data for experiment...")
normal_data = np.load("processed_data/normal_binary.npy")[:20000] # Train on first 20k
fault_data = np.load(TARGET_FILE)[:20000]

print(f"🚀 Starting Monte Carlo Experiment ({RUNS} runs)...")
print("-" * 60)

results = []

# --- THE LOOP ---
for i in range(RUNS):
    # Call the engine
    result = cgp_engine.evolve_reflex(
        run_id=i+1, 
        normal_data=normal_data, 
        fault_data=fault_data, 
        generations=GENERATIONS,
        penalty_factor=PENALTY
    )
    results.append(result)

print("-" * 60)
print("📊 EXPERIMENT COMPLETE. ANALYZING CHAMPIONS...")

# Filter out broken circuits (Recall near 0)
valid_results = [r for r in results if r['recall'] > 0.05]

if not valid_results:
    print("❌ All runs failed to find a valid circuit. Try lowering Penalty or increasing Generations.")
else:
    # Sort by Score (best first)
    valid_results.sort(key=lambda x: x['score'], reverse=True)
    champion = valid_results[0]
    
    print(f"\n🏆 ULTIMATE CHAMPION (Run {champion['id']})")
    print(f"   Recall:      {champion['recall']:.4f}%")
    print(f"   Efficiency:  {champion['efficiency']:.2f}% (Captured Fault Energy)")
    print(f"   False Alarm: {champion['fpr']:.4f}%")
    print(f"   Fitness:     {champion['score']:.4f}")
    
    # Save the best one for VHDL export later
    best_global = champion['circuit']
    print("\n✅ 'best_global' variable has been updated with the Champion circuit.")
    print("   You can now run the VHDL generator script.")