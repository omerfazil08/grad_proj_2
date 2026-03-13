import numpy as np

# Load your data
normal_data = np.load("processed_data/normal_binary.npy")
fault_data = np.load("processed_data/inner_race_binary.npy")

# Configuration
WINDOW_SIZE = 16
NUM_SAMPLES = 1000  # Let's simulate the first 1000 cycles (enough to see the fault)

def export_vectors(data, filename):
    with open(filename, "w") as f:
        # We need to manually slide the window to match hardware shift register behavior
        for i in range(NUM_SAMPLES):
            # Extract window of 16 bits
            if i + WINDOW_SIZE < len(data):
                window = data[i : i+WINDOW_SIZE]
                
                # Convert [0, 1, 0...] to string "010..."
                # Important: VHDL array index 0 is on the RIGHT (LSB), 
                # but Python index 0 is LEFT. We must reverse to match "downto 0".
                # window[0] is oldest (t-16), window[15] is newest (t).
                # standard logic vector (15 downto 0) -> MSB is 15.
                # So Python window[15] should be on the left of the string? 
                # Actually, standard convention: String "1000" -> 1 is MSB (15).
                # So we flip it: newest sample (window[-1]) is MSB.
                
                window_str = "".join(str(x) for x in window[::-1])
                f.write(window_str + "\n")
                
    print(f"✅ Generated {filename} with {NUM_SAMPLES} vectors.")

# Export Fault Data (so we can see the alarm trigger)
export_vectors(fault_data, "reflex_vectors.txt")