import asyncio
import pytest
from process_monitor import monitor_process, hash_folder
from start_arcanum import arcanum_page
import tempfile
from functools import partial
import os

@pytest.mark.asyncio
async def test_restart_behavior():
    # Simulated shared value
    monitored_value = 0  # Global variable to simulate retrieval
    start_process = 0

    def retrieve_value():
        return monitored_value  # This function will be passed as the monitor function
    
    @monitor_process(retrieve_value, timeout=5)
    async def process_a():
        """Simulated process with workers modifying a shared value."""
        nonlocal monitored_value
        workers = [asyncio.create_task(worker(i)) for i in range(3, 5)]
        await asyncio.gather(*workers)

    async def worker(threshold):
        nonlocal monitored_value
        nonlocal start_process
        start_process = monitored_value
        i = 0
        while True:
            await asyncio.sleep(1)
            if monitored_value > 9:
                break  # Stop if value exceeds 10
            i += 1
            if i < threshold:
                monitored_value += 1
                print(f"Worker {i}<{threshold} updated value: {monitored_value}")
            else:
                print(f"Worker {i}>{threshold}: unresponsive")
        print(f"Worker with threshold {threshold} finished.")
        return

    async def main():
        """Main entry point for the event loop."""
        await process_a()  # Start monitored process

    await main()

    assert monitored_value == 10  # Assert that the process was restarted
    assert start_process == 5  # 3: updates 2 times, 4: updates 3 times before quitting > 5

@pytest.mark.asyncio
async def test_restart_browser():
    i = 0
    write_file = True
    n_open = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        async def worker(name):
            nonlocal i
            nonlocal write_file
            nonlocal temp_dir
            nonlocal n_open

            while i < 5:
                i += 1
                async with arcanum_page(headless=False) as page:
                    n_open += 1
                    await page.goto("https://adt.arcanum.com/en/discover/")
                    await asyncio.sleep(2)
                    if write_file:
                        with open(temp_dir + "/test" + name + ".txt", "w") as f:
                            f.write("Hello, World!")
                        print("writing")
                        write_file = False
            print(f"Worker {name} finished. {i=}")
            return

                
        hash_temp_folder = partial(hash_folder, temp_dir)

        @monitor_process(hash_temp_folder, timeout=5)
        async def process_a():
            """Simulated process with workers modifying a shared value."""
            workers = [asyncio.create_task(worker(str(i))) for i in range(3, 5)]
            await asyncio.gather(*workers)

        async def main():
            """Main entry point for the event loop."""
            await process_a()

        await main()

        assert i == 5  # Assert that the process was restarted
        assert len(os.listdir(temp_dir)) == 1
        assert n_open == 4

            

