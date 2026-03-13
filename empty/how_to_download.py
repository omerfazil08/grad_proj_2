import os
import urllib.request

# The base URL for the CWRU dataset
BASE_URL = "https://engineering.case.edu/sites/default/files"

# The 4 specific files we need for your Thesis Stage 1
FILES_TO_DOWNLOAD = {
    "97.mat":  "/97.mat",   # Normal
    "105.mat": "/105.mat",  # Inner Race 0.007
    "118.mat": "/118.mat",  # Ball 0.007
    "130.mat": "/130.mat"   # Outer Race 0.007
}

DOWNLOAD_DIR = "raw_data"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

print(f"🚀 Starting download into '{DOWNLOAD_DIR}' folder...")

for filename, url_suffix in FILES_TO_DOWNLOAD.items():
    full_url = BASE_URL + url_suffix
    save_path = os.path.join(DOWNLOAD_DIR, filename)
    
    print(f"   ⬇️  Downloading {filename}...", end=" ")
    try:
        urllib.request.urlretrieve(full_url, save_path)
        print("Done! ✅")
    except Exception as e:
        print(f"Failed! ❌ ({e})")

print("\nAll files downloaded. You can now run the data_loader.py script.")