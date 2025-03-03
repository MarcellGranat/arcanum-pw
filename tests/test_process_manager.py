import asyncio
import pytest
from process_manager import ProcessManager

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

    def preprocess():
        nonlocal n_restart
        output = [_ + n_restart for _ in delays]
        n_restart += 2
        return output
    
    process = ProcessManager(preprocess=preprocess, func=wait_and_add, items=items, check_function=always_rerun, timeout=9)
    # * puts to the end of the queue if the task is cancelled > 2nd 5 sec is over 9 sec > 'date' is at the end of the queue
    expected_results = ['4apple', '5banana', '4cherry', '6fig', '7elderberry', '8date']
    results = await process.run()
    assert results == expected_results