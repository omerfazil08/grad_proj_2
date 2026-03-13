import numpy as np

files = {
    "processed_data/normal_binary.npy": "Normal Baseline",
    "processed_data/inner_race_binary.npy": "Inner Race Fault",
    "processed_data/ball_binary.npy": "Ball Fault",
    "processed_data/outer_race_binary.npy": "Outer Race Fault"
}

print(f"{'Condition':<20} | {'Total Bits':<12} | {'Activity (Burst %)'}")
print("-" * 55)

results = {}
for filename, label in files.items():
    try:
        data = np.load(filename)
        # Calculate percentage of 1s
        activity_percent = np.mean(data) * 100
        results[label] = activity_percent
        print(f"{label:<20} | {len(data):<12} | {activity_percent:.4f}%")
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")