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
    """Decorator that monitors a process and restarts it if it is stuck, but stops if the process exits naturally."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_value = check_function()
            process_task = asyncio.create_task(func(*args, **kwargs))

            while not process_task.done():  # Monitor while process is running
                await asyncio.sleep(timeout)

                if process_task.done():  # If process has exited, stop monitoring
                    logger.success(f"Monitor: {func.__name__} finished naturally. Stopping monitor.")
                    break

                current_value = check_function()
                if current_value == last_value:  # If monitored value is unchanged
                    logger.warning(f"Process {func.__name__} seems unresponsive. Restarting...")
                    process_task.cancel()
                    try:
                        await process_task  # Cleanup
                    except asyncio.CancelledError:
                        pass
                    process_task = asyncio.create_task(func(*args, **kwargs))  # Restart process
                
                last_value = current_value  # Update the last observed value

            logger.success(f"Monitor: {func.__name__} finished, stopping monitor.")
        
        return wrapper
    return decorator