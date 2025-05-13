import asyncio
from loguru import logger

logger.add("logs", rotation="1 week")

class ProcessManager:
    def __init__(self, preprocess, func, items, check_function=None, timeout=300):
        self.preprocess = preprocess
        self.func = func
        self.items = items
        self.check_function = check_function
        self.timeout = timeout
        self.results = []
        self.tasks = []
        self._queue = None

    @property
    async def queue(self):
        """Fill the queue with tasks."""
        if self._queue is None:
            self._queue = asyncio.Queue()
            for item in self.items:
                await self._queue.put(item)
        return self._queue

    async def worker(self, config):
        """Worker that processes items from the queue."""
        while True:
            try:
                if (await self.queue).empty():
                    return
                item = await (await self.queue).get()
                try:
                    result = await self.func(config, item)
                    self.results.append(result)
                    (await self.queue).task_done()
                except asyncio.CancelledError:
                    # Put the item back into the queue if the task is cancelled
                    await (await self.queue).put(item)
                    raise
            except asyncio.CancelledError:
                break

    @property
    async def configs(self):
        """Execute tasks in parallel with specified delays."""
        return self.preprocess()

    async def create_workers(self):
        """Create workers."""
        configs = await self.configs
        return [asyncio.create_task(self.worker(config)) for config in await configs]

    async def check_and_restart_workers(self):
        """Check the condition and restart workers if needed."""
        while True:
            await asyncio.sleep(1)
            if all(task.done() for task in self.tasks) and (await self.queue).empty():
                logger.success("All tasks are done.")
                return
            await asyncio.sleep(self.timeout)
            if self.check_function and await self.check_function():
                logger.warning("Process seems unresponsive. Restarting workers.")
                for task in self.tasks:
                    task.cancel()
                await asyncio.gather(*self.tasks, return_exceptions=True)
                self.tasks = await self.create_workers()

    async def run(self):
        """Run the process manager."""
        self.tasks = await self.create_workers()
        check_task = asyncio.create_task(self.check_and_restart_workers())
        await asyncio.gather(check_task, *self.tasks)
        # Wait for all tasks to complete
        await asyncio.gather(*self.tasks)
        return self.results