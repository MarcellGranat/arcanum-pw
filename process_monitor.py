import asyncio
import functools
from loguru import logger
import os
import xxhash

logger.add("logs")

def hash_file(filepath: str, hasher=xxhash.xxh64()):
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

def monitor_process(check_function, timeout=300):
    """Decorator that monitors a process and restarts it if the check_function returns the same value for `timeout` seconds."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_value = check_function()  # Get initial monitored value
            process_task = asyncio.create_task(func(*args, **kwargs))  # Start the process

            while not process_task.done():  # Keep monitoring while process is running
                await asyncio.sleep(timeout)  # Wait for `timeout` seconds

                current_value = check_function()  # Get updated value
                if current_value == last_value:  # Value unchanged
                    logger.warning(f"Process {func.__name__} seems unresponsive. Restarting...")
                    process_task.cancel()
                    try:
                        await process_task  # Ensure cleanup
                    except asyncio.CancelledError:
                        pass
                    process_task = asyncio.create_task(func(*args, **kwargs))  # Restart process
                
                last_value = current_value  # Update last observed value
            
            logger.success(f"Monitor: {func.__name__} finished, stopping monitor.")
        
        return wrapper
    return decorator