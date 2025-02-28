import asyncio
import pytest
from process_manager import ProcessManager
from start_arcanum import arcanum_page
from archive_links import generate_archive_links

async def wait_and_add(delay, item):
    """Wait for a specified delay and then concatenate the delay and item."""
    print(f"Waiting for {delay} seconds.")
    await asyncio.sleep(delay + 0.1)
    result = f"{delay}{item}"
    return result

async def always_rerun():
    return True  # Change this to True to stop the process after 5 seconds

@pytest.mark.asyncio
async def test_restart():
    
    items = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig'] 
    delays = [4, 5]
    
    n_restart = 0

    async def preprocess():
        nonlocal n_restart
        output = [_ + n_restart for _ in delays]
        n_restart += 2
        return output
    
    process = ProcessManager(preprocess=preprocess, func=wait_and_add, items=items, check_function=always_rerun, timeout=9)
    expected_results = ['4apple', '5banana', '4cherry', '6date', '7elderberry', '8fig']
    results = await process.run()
    print(results)
    assert results == expected_results
