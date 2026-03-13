import numpy as np
import scipy.io
import os
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# We use the raw "Inner Race" file as our calibration target
# (Because if you can see the Inner Race fault, you can usually see the others)
CALIBRATION_FILE = "raw_data/105.mat"
KEY_NAME = "X105_DE_time"

# Scan Range (k-factor)
# We look from 1 sigma (very sensitive) to 10 sigma (very deaf)
K_MIN = 1.0
K_MAX = 10.0
STEPS = 50

# Target Density: We want the binary stream to be active ~3% of the time.
# This implies sharp, distinct spikes (Morse Code), not constant noise.
TARGET_DENSITY = 0.03  # 3%


def load_raw_signal(file_path, key):
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return None
    try:
        mat = scipy.io.loadmat(file_path)
        signal = mat[key].flatten()
        return signal
    except KeyError:
        print(f"❌ Error: Key {key} not found in mat file.")
        return None


def auto_tune():
    print(f"🔬 STARTING AUTO-TUNER (Algorithm 1)...")
    print(f"   Target: {CALIBRATION_FILE}")

    # 1. Load Data
    raw_signal = load_raw_signal(CALIBRATION_FILE, KEY_NAME)
    if raw_signal is None: exit()

    # 2. Calculate Base Stats (The "Physics" of the signal)
    # Note: In real hardware, 'Mean' is your DC offset (usually 0V or 1.65V)
    # 'RMS' is the AC energy.
    mu = np.mean(raw_signal)
    sigma = np.std(raw_signal)

    print(f"   Signal Mean (DC): {mu:.4f}")
    print(f"   Signal Std Dev (RMS): {sigma:.4f}")
    print("-" * 40)

    best_k = 0
    best_diff = 9999
    best_density = 0

    results_k = []
    results_density = []

    # 3. The Sweep Loop
    print(f"   Scanning thresholds...")

    for k in np.linspace(K_MIN, K_MAX, STEPS):
        # Calculate Threshold
        threshold = mu + (k * sigma)

        # Apply Threshold (Simulate the Comparator)
        # In hardware: If Voltage > Threshold -> 1
        binary_stream = (np.abs(raw_signal) > threshold).astype(int)

        # Calculate Density (% of time signal is HIGH)
        density = np.mean(binary_stream)

        # Store for plotting
        results_k.append(k)
        results_density.append(density)

        # Compare to Target (Goldilocks Check)
        diff = abs(density - TARGET_DENSITY)
        if diff < best_diff:
            best_diff = diff
            best_k = k
            best_density = density

    # 4. The Verdict
    print("-" * 40)
    print(f"✅ CALIBRATION COMPLETE")
    print(f"   Optimal K-Factor: {best_k:.2f}")
    print(f"   Resulting Density: {best_density * 100:.2f}% (Target: {TARGET_DENSITY * 100}%)")

    # 5. Hardware Translation
    # This tells you what to set your Potentiometer to!
    # Assumption: Standard Piezo Sensitivity.
    # If using CWRU raw units (which are effectively g's or Volts depending on gain):
    optimal_voltage = mu + (best_k * sigma)

    print(f"\n🔧 HARDWARE SETTING:")
    print(f"   Set your Potentiometer Voltage to: {optimal_voltage:.4f} Units")
    print("   (Note: 'Units' matches your sensor output. If CWRU is Volts, this is Volts.)")

    # 6. Plot the Curve (The "Eye Exam" Chart)
    plt.figure(figsize=(8, 4))
    plt.plot(results_k, results_density, label='Signal Density')
    plt.axhline(y=TARGET_DENSITY, color='r', linestyle='--', label='Target (3%)')
    plt.axvline(x=best_k, color='g', linestyle='--', label=f'Optimal K={best_k:.2f}')
    plt.title("Algorithm 1: Finding the Optimal Threshold")
    plt.xlabel("Threshold Factor (k)")
    plt.ylabel("Activity Density")
    plt.legend()
    plt.grid(True)
    plt.savefig("calibration_curve.png")
    print("   📸 Calibration curve saved to 'calibration_curve.png'")


if __name__ == "__main__":
    auto_tune()