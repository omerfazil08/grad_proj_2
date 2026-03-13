
import scipy.io

file_checks = {
    "97.mat": "X097_DE_time",
    "105.mat": "X105_DE_time",
    "118.mat": "X118_DE_time",
    "130.mat": "X130_DE_time"
}

results = {}

for filename, expected_key in file_checks.items():
    try:
        # Load the file
        mat = scipy.io.loadmat(filename)
        
        # Check if the key exists
        keys = list(mat.keys())
        if expected_key in keys:
            results[filename] = f"✅ Valid (Found {expected_key})"
        else:
            # Sometimes keys differ (e.g., X097_DE_time vs DE_time), we check for partial match
            found = [k for k in keys if "DE_time" in k]
            if found:
                results[filename] = f"⚠️ Key Mismatch (Found {found[0]}, expected {expected_key})"
            else:
                results[filename] = f"❌ Invalid (No DE_time key found. Keys: {keys[:5]}...)"
                
    except Exception as e:
        results[filename] = f"❌ Corrupted or Not a MAT file ({str(e)})"

print(results)