import os
import xxhash

def hash_file(filepath: str = "download_log.json", hasher=xxhash.xxh64()):
    """Compute a fast hash for a given file."""
    hasher = hasher.copy()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def hash_folder(folder_path: str = "data"):
    """Compute a combined hash of all files in a folder (recursively)."""
    hasher = xxhash.xxh64()
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):  # Sorting ensures consistent order
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            hasher.update(file_hash.encode())  # Aggregate hashes
    return hasher.hexdigest()
