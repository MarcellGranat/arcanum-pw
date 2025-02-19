import asyncio
import pytest
from loguru import logger
from parallel_execution import parallel_exec
from start_arcanum import generate_usernames, read_cookies, arcanum_page
from archive_links import generate_archive_links

async def wait_and_add(delay, item):
    """Wait for a specified delay and then concatenate the delay and item."""
    print(f"Waiting for {delay} seconds.")
    await asyncio.sleep(delay + 0.1)
    result = f"{delay}{item}"
    return result

logger.add("parallel_execution.log", level="INFO")

@pytest.mark.asyncio
async def test_parallel_exec():
    items = ['apple', 'banana', 'cherry', 'date']
    delays = [1, 3]
    results = await parallel_exec(wait_and_add, delays, items)
    assert len(results) == len(items)
    assert results == ['1apple', '1cherry', '3banana', '1date']

async def visit_page(username, url):
    cookie = read_cookies(username)
    async with arcanum_page(cookie, headless=False, slow_mo=2000) as page:
        print(url)
        await page.goto(url)
        title = await page.title()
        return f"{username} visited: {title} ({url})"
    
@pytest.mark.asyncio
async def test_parallel_exec_arcanum():
    urls = [url for name, url in generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/")][:6]
    usernames = list(generate_usernames())
    results = await parallel_exec(visit_page, generate_usernames(), urls)
    assert len(results) == len(urls)
    assert all("visited" in result for result in results)
    assert all(username in result for username, result in zip(usernames, results))
