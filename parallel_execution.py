import asyncio

async def worker(func, config, queue, results):
    """Worker that processes items from the queue."""
    while True:
        try:
            item = await queue.get()
            result = await func(config, item)
            results.append(result)
            queue.task_done()
        except asyncio.CancelledError:
            break

async def parallel_exec(func, configs, items):
    """Execute tasks in parallel with specified delays."""
    queue = asyncio.Queue()
    results = []

    # Fill the queue with tasks
    for item in items:
        await queue.put(item)

    # Create workers
    workers = [asyncio.create_task(worker(func, config, queue, results)) for config in configs]

    # Wait until all tasks are processed
    await queue.join()

    # Cancel remaining workers
    for w in workers:
        w.cancel()

    # Wait until all workers are cancelled
    await asyncio.gather(*workers, return_exceptions=True)
    print("All workers are done.")
    return results
