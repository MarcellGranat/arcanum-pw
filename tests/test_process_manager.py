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
    await asyncio.sleep(5)
    return True  # Change this to True to stop the process after 5 seconds

@pytest.mark.asyncio
async def test_parallel_exec():
    
    items = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honeydew', 'imbe']
    delays = [1, 3]
    
    def preprocess():
        return delays
    
    process = ProcessManager(preprocess=preprocess, func=wait_and_add, items=items, check_function=always_rerun, timeout=5)
    results = await process.run()
    
    assert results == ['1apple', '1cherry', '3banana', '1date', '1fig', '1grape', '3elderberry', '1honeydew', '3imbe']

async def visit_page(username, url):
    async with arcanum_page(headless=True, slow_mo=2000) as page:
        await page.goto(url)
        title = await page.title()
        print(f"{username} visited: {title} ({url})")
        return f"{username} visited: {title} ({url})"
    
@pytest.mark.asyncio
async def test_parallel_exec_arcanum():
    urls = [url for name, url in generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/")][:8]
    def users():
        yield from ["bear", "bull", "cat"]

    usernames = list(users())
    process = ProcessManager(preprocess=users, func=visit_page, items=urls, check_function=None, timeout=5)
    results = await process.run()
    print(results)
    assert all(username in result for username, result in zip(usernames, results))
