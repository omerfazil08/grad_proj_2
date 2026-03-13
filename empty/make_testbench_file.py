import numpy as np

# Configuration
OUTPUT_FILE = "simulation_input.txt"
WINDOW_SIZE = 16
SAMPLES_PER_SEGMENT = 1000  # Short enough to run fast, long enough to trip alarm


def create_sliding_windows(data):
    """Converts 1D binary stream into 16-bit sliding window strings"""
    vectors = []
    # Sliding window logic
    for i in range(len(data) - WINDOW_SIZE + 1):
        window = data[i: i + WINDOW_SIZE]
        # Reverse to match VHDL (newest bit at index 0 or 15 depending on convention)
        # We assume standard shift register: Newest bit enters LSB or MSB.
        # Let's map: window[0] (oldest) -> MSB, window[-1] (newest) -> LSB
        vec_str = "".join(str(int(x)) for x in window)
        vectors.append(vec_str)
    return vectors


print("🚀 Building Director's Cut Simulation File...")

try:
    # 1. Load Data
    normal = np.load("processed_data/normal_binary.npy")[:SAMPLES_PER_SEGMENT]
    outer = np.load("processed_data/outer_race_binary.npy")[:SAMPLES_PER_SEGMENT]
    inner = np.load("processed_data/inner_race_binary.npy")[:SAMPLES_PER_SEGMENT]
    ball = np.load("processed_data/ball_binary.npy")[:SAMPLES_PER_SEGMENT]

    # 2. Stitch the "Story"
    # Sequence: Normal -> Outer -> Normal -> Inner -> Normal -> Ball
    mixed_stream = np.concatenate([
        normal,
        outer,
        normal,
        inner,
        normal,
        ball
    ])

    print(f"   Combined Stream Length: {len(mixed_stream)} bits")

    # 3. specific Logic for VHDL
    vectors = create_sliding_windows(mixed_stream)

    # 4. Save to text file
    with open(OUTPUT_FILE, "w") as f:
        for v in vectors:
            f.write(v + "\n")

    print(f"✅ Saved {len(vectors)} test vectors to {OUTPUT_FILE}")
    print("   Copy this file to your Vivado project folder (project_name.sim/sim_1/behav/xsim/)")

except FileNotFoundError:
    print("❌ Error: Processed data files not found. Run data_loader.py first.")