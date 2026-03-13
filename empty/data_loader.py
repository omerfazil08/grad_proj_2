import numpy as np
import scipy.io
import os
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
FILE_CONFIG = {
    "normal": {"filename": "97.mat", "key": "X097_DE_time"},
    "inner_race": {"filename": "105.mat", "key": "X105_DE_time"},
    "ball": {"filename": "118.mat", "key": "X118_DE_time"},
    "outer_race": {"filename": "130.mat", "key": "X130_DE_time"}
}

DATA_DIR = "raw_data"
SAVE_DIR = "processed_data"

# --- THE "EDGE CATCHER" SETTINGS ---
# K=3.5 is the "Standard" for outlier detection (3.5 sigma)
# Window=50 samples covers about 4ms, enough to capture the "Envelope"
ADAPTIVE_K = 2.57
WINDOW_SIZE = 150


def load_raw_signal(file_path, key_name):
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return None
    try:
        mat_data = scipy.io.loadmat(file_path)
        return mat_data[key_name].flatten()
    except KeyError:
        return None


def adaptive_edge_catcher(signal, window, k):
    """
    Simulates a Data Slicer / Envelope Detector circuit.
    Logic: Is the current signal (rectified) much larger than the local average?
    """
    # 1. Full Wave Rectifier (Hardware: Diode Bridge)
    rectified = np.abs(signal - np.mean(signal))  # Remove DC, then Abs

    # 2. Envelope Detector (Hardware: RC Circuit / Low Pass Filter)
    # We use a simple convolution to simulate the capacitor charging/discharging
    # This creates the "Moving Average" or "Threshold Line"
    # Note: 'valid' mode prevents edge artifacts, but shrinks array slightly.
    # We use 'same' to keep size.
    avg_kernel = np.ones(window) / window
    envelope = np.convolve(rectified, avg_kernel, mode='same')

    # 3. Comparator (Hardware: LM393)
    # Compare "Instant Voltage" vs "Envelope Voltage * Gain"
    threshold_curve = envelope * k

    # 4. The Output Stream
    binary_bits = (rectified > threshold_curve).astype(int)

    return binary_bits, threshold_curve, rectified


def run_pipeline():
    print(f"🚀 RESTARTING PIPELINE: ADAPTIVE EDGE CATCHER")
    print(f"   Logic: Data Slicer (Envelope Detection)")
    print("-" * 50)

    os.makedirs(SAVE_DIR, exist_ok=True)

    for label, config in FILE_CONFIG.items():
        path = os.path.join(DATA_DIR, config["filename"])
        raw_signal = load_raw_signal(path, config["key"])
        if raw_signal is None: continue

        # Apply Adaptive Processing
        binary_bits, thresh_curve, rectified_sig = adaptive_edge_catcher(raw_signal, WINDOW_SIZE, ADAPTIVE_K)

        # Save
        save_path = os.path.join(SAVE_DIR, f"{label}_binary.npy")
        np.save(save_path, binary_bits)

        # Check Density (Should be non-zero for all faults!)
        density = np.mean(binary_bits) * 100
        print(f"   ✅ Processed {label:12s} | Density: {density:.2f}% | Saved.")

        # Verification Plot
        plt.figure(figsize=(10, 4))
        limit = 1000
        plt.plot(rectified_sig[:limit], label='Rectified Signal (Abs)', color='skyblue', alpha=0.8)
        plt.plot(thresh_curve[:limit], label='Envelope Threshold', color='red', linestyle='--')
        plt.fill_between(range(limit), 0, np.max(rectified_sig[:limit]),
                         where=(binary_bits[:limit] == 1), color='black', alpha=0.1, label='Output')
        plt.title(f"Edge Catcher Verification: {label}")
        plt.legend()
        plt.savefig(os.path.join(SAVE_DIR, f"{label}_verify.png"))
        plt.close()


if __name__ == "__main__":
    run_pipeline()