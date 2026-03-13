import numpy as np
import scipy.io
import os
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# We calibrate on Inner Race because it is the "Standard" fault.
# If we can catch this, we can catch everything.
CALIBRATION_FILE = "raw_data/105.mat"
KEY_NAME = "X105_DE_time"

# Optimization Target
# We want the 'Edge Catcher' to fire ~3% of the time (The Physics Constant)
TARGET_DENSITY = 0.03

# Sweep Settings
K_MIN = 1.0
K_MAX = 10.0
STEPS = 50
WINDOW_SIZE = 150  # 4ms window (Physical constant for this motor speed)


def load_raw_signal(file_path, key):
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return None
    try:
        mat = scipy.io.loadmat(file_path)
        return mat[key].flatten()
    except KeyError:
        return None


def adaptive_edge_catcher_simulation(signal, window, k):
    """
    The exact logic from data_loader.py, but used for tuning.
    """
    # 1. Rectify (Diode)
    rectified = np.abs(signal - np.mean(signal))

    # 2. Envelope (RC Filter)
    avg_kernel = np.ones(window) / window
    envelope = np.convolve(rectified, avg_kernel, mode='same')

    # 3. Comparator (Slicer)
    # Logic: Is Signal > (Average * K)?
    threshold_curve = envelope * k
    binary_bits = (rectified > threshold_curve).astype(int)

    return binary_bits


def tune():
    print(f"🔬 STARTING ADAPTIVE AUTO-TUNER...")
    print(f"   Target: {CALIBRATION_FILE}")
    print(f"   Goal: Find 'K' for {TARGET_DENSITY * 100}% Density")
    print("-" * 40)

    raw_signal = load_raw_signal(CALIBRATION_FILE, KEY_NAME)
    if raw_signal is None: exit()

    best_k = 0
    best_diff = 9999
    best_density = 0

    results_k = []
    results_density = []

    # The Sweep Loop
    for k in np.linspace(K_MIN, K_MAX, STEPS):
        # Run the full Edge Catcher logic
        binary_bits = adaptive_edge_catcher_simulation(raw_signal, WINDOW_SIZE, k)

        # Check result
        density = np.mean(binary_bits)

        results_k.append(k)
        results_density.append(density)

        # Compare to Target
        diff = abs(density - TARGET_DENSITY)
        if diff < best_diff:
            best_diff = diff
            best_k = k
            best_density = density

            # Live print for sanity check
            # print(f"   Testing K={k:.2f} -> Density={density*100:.2f}%")

    print("-" * 40)
    print(f"✅ TUNING COMPLETE")
    print(f"   Optimal Adaptive K: {best_k:.2f}")
    print(f"   Resulting Density:  {best_density * 100:.2f}%")
    print("-" * 40)
    print(f"🚀 NEXT STEP:")
    print(f"   Update 'ADAPTIVE_K = {best_k:.2f}' in your data_loader.py")

    # Plot curve
    plt.figure(figsize=(8, 4))
    plt.plot(results_k, results_density, label='Density vs K')
    plt.axhline(y=TARGET_DENSITY, color='r', linestyle='--', label='Target (3%)')
    plt.axvline(x=best_k, color='g', linestyle='--', label=f'Optimal K={best_k:.2f}')
    plt.title("Tuning the Adaptive Edge Catcher")
    plt.xlabel("Sensitivity Factor (K)")
    plt.ylabel("Signal Density")
    plt.grid(True)
    plt.legend()
    plt.savefig("tuning_curve.png")


if __name__ == "__main__":
    tune()