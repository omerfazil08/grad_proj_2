import numpy as np
import scipy.io
import os
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# The standard keys in CWRU .mat files are messy. 
# We map them explicitly to avoid "KeyError".
FILE_CONFIG = {
    "normal":     {"filename": "97.mat",  "key": "X097_DE_time"},  # Normal Baseline
    "inner_race": {"filename": "105.mat", "key": "X105_DE_time"}, # Inner Race Fault
    "ball":       {"filename": "118.mat", "key": "X118_DE_time"}, # Ball Fault
    "outer_race": {"filename": "130.mat", "key": "X130_DE_time"}  # Outer Race Fault
}

DATA_DIR = "raw_data"  # Put your .mat files in this folder
SAVE_DIR = "processed_data"

def load_and_process(file_path, key_name, label_name):
    """
    1. Loads raw .mat file
    2. Extracts the Drive End (DE) signal
    3. Applies Adaptive Thresholding (Stage 1 Hardware Logic)
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return None

    # Load MATLAB file
    mat_data = scipy.io.loadmat(file_path)
    
    # Extract vibration array (usually shape is (N, 1))
    try:
        raw_signal = mat_data[key_name].flatten()
        print(f"✅ Loaded {label_name}: {len(raw_signal)} samples")
    except KeyError:
        print(f"❌ Key {key_name} not found in {file_path}. Check file content.")
        return None

    return raw_signal

def adaptive_threshold_processing(signal, window_size=50, k_factor=3.5):
    """
    Simulates the Hardware Adaptive Threshold (Running RMS).
    Formula: Threshold(t) = Mean + k * RMS(window)
    """
    # 1. Remove DC Offset (Hardware High-pass filter equivalent)
    signal = signal - np.mean(signal)
    
    # 2. Calculate Running RMS (Inefficient in Python, but accurate for sim)
    # We use pandas for speed if available, else numpy
    squared = np.power(signal, 2)
    window = np.ones(window_size) / window_size
    # Convolution is a fast way to do "Moving Average"
    moving_energy = np.convolve(squared, window, mode='same')
    moving_rms = np.sqrt(moving_energy)
    
    # 3. Define Threshold Curve
    # In hardware, K is a bit-shift or multiplier. Here we use float.
    threshold_curve = k_factor * moving_rms
    
    # 4. Binarize
    # Logic: If |signal| > threshold -> 1, else 0
    binary_stream = (np.abs(signal) > threshold_curve).astype(int)
    
    return binary_stream, threshold_curve

def run_pipeline():
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    for label, config in FILE_CONFIG.items():
        path = os.path.join(DATA_DIR, config["filename"])
        
        # A. Load
        raw_signal = load_and_process(path, config["key"], label)
        if raw_signal is None: continue
        
        # B. Process (Adaptive Threshold)
        # We use K=3.5 (standard starting point for "3-sigma" outlier detection)
        binary_bits, thresh_curve = adaptive_threshold_processing(raw_signal, window_size=64, k_factor=3.5)
        
        # C. Save
        save_path = os.path.join(SAVE_DIR, f"{label}_binary.npy")
        np.save(save_path, binary_bits)
        print(f"   💾 Saved binary stream to {save_path}")
        
        # D. Visualization (Critical for Thesis Validation)
        # We plot only the first 1000 samples to verify it looks like an "eye reflex"
        plt.figure(figsize=(10, 4))
        plt.plot(raw_signal[:1000], label='Raw Vibration', alpha=0.5)
        plt.plot(thresh_curve[:1000], 'r--', label='Adaptive Threshold')
        # Scale binary to make it visible on plot
        plt.plot(binary_bits[:1000] * np.max(raw_signal[:1000]), 'k', linewidth=0.5, label='Output Bits')
        plt.title(f"Preprocessing Verification: {label}")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(SAVE_DIR, f"{label}_verify.png"))
        plt.close()

if __name__ == "__main__":
    run_pipeline()