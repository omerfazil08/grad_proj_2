import numpy as np
import scipy.io
import os
import pandas as pd

# --- CONFIGURATION ---
FILE_CONFIG = {
    "inner_race": {"filename": "105.mat", "key": "X105_DE_time"},
    "ball": {"filename": "118.mat", "key": "X118_DE_time"},
    "outer_race": {"filename": "130.mat", "key": "X130_DE_time"}
}

DATA_DIR = "raw_data"
TARGET_DENSITY = 0.03  # 3% Target
WINDOW_SIZE = 150  # The new "Lazy" window size
K_MIN = 1.0
K_MAX = 8.0
STEPS = 50


def load_signal(file_path, key):
    try:
        mat = scipy.io.loadmat(file_path)
        return mat[key].flatten()
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def get_density_for_k(signal, k):
    """Calculates density for a specific K value."""
    # 1. Rectify
    rectified = np.abs(signal - np.mean(signal))
    # 2. Envelope (Moving Average)
    avg_kernel = np.ones(WINDOW_SIZE) / WINDOW_SIZE
    envelope = np.convolve(rectified, avg_kernel, mode='same')
    # 3. Comparator
    threshold = envelope * k
    binary = (rectified > threshold).astype(int)
    return np.mean(binary)


def find_optimal_k(label, signal):
    """Sweeps K to find the value that yields ~3% density."""
    best_k = 0
    best_diff = 1.0

    # Coarse Sweep
    for k in np.linspace(K_MIN, K_MAX, STEPS):
        d = get_density_for_k(signal, k)
        diff = abs(d - TARGET_DENSITY)
        if diff < best_diff:
            best_diff = diff
            best_k = k

    return best_k


def run_analysis():
    print(f"🔬 ANALYZING SIGNAL STRENGTH (Window={WINDOW_SIZE})")
    print(f"   Target Density: {TARGET_DENSITY * 100}%")
    print("-" * 60)
    print(f"{'FAULT TYPE':<15} | {'OPTIMAL K':<12} | {'SENSITIVITY REQ'}")
    print("-" * 60)

    results = []

    for label, config in FILE_CONFIG.items():
        path = os.path.join(DATA_DIR, config["filename"])
        sig = load_signal(path, config["key"])

        if sig is not None:
            opt_k = find_optimal_k(label, sig)

            # Interpretation
            # Low K = Weak Signal (Needs high sensitivity/low threshold to be seen)
            # High K = Strong Signal (Can be seen easily even with high threshold)
            sensitivity = "HIGH (Weak Signal)" if opt_k < 3.0 else "LOW (Strong Signal)"

            print(f"{label:<15} | {opt_k:.2f}         | {sensitivity}")
            results.append((label, opt_k))

    print("-" * 60)

    # Logic to pick the winner
    # We must choose the MINIMUM K found across all files.
    # Why? A system set to K=2.0 will see K=4.0 faults easily.
    # But a system set to K=4.0 will be blind to K=2.0 faults.

    weakest_fault, min_k = min(results, key=lambda x: x[1])

    print(f"📢 CONCLUSION:")
    print(f"   The WEAKEST link is: '{weakest_fault.upper()}'")
    print(f"   It requires K = {min_k:.2f} to be visible.")
    print(f"   👉 Set ADAPTIVE_K = {min_k:.2f} in data_loader.py")
    print(f"   (This ensures {weakest_fault} is detected, while others will appear 'louder')")


if __name__ == "__main__":
    run_analysis()