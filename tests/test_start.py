import start_arcanum
import pytest
import time
import asyncio
import json
import cookie_from_txt
import tempfile

async def main_page_title():
    async with start_arcanum.arcanum_page() as page:
        await page.goto("https://adt.arcanum.com/hu/")
        title = await page.title()
        return title

@pytest.mark.asyncio
async def test_title():
    title = await main_page_title()
    assert title == "Arcanum Újságok"

async def execution_time_single():
    start = time.time()
    await main_page_title()
    end = time.time()
    return end - start

async def execution_time_parallel():
    start = time.time()
    await asyncio.gather(main_page_title(), main_page_title())
    end = time.time()
    return end - start

@pytest.mark.asyncio
async def test_execution_time():
    single_time = await execution_time_single()
    parallel_time = await execution_time_parallel()
    assert single_time * 1.3 > parallel_time

@pytest.mark.asyncio
async def test_login():
    username = "marcigranat"
    cookie = start_arcanum.read_cookies(username)

    async with start_arcanum.arcanum_page(cookie=cookie) as page:
        await page.goto("https://adt.arcanum.com/hu/")
        logged_in_as = await page.locator('ul.navbar-nav.ms-auto.me-2 li.nav-item.dropdown a.btn.btn-outline-primary strong').get_attribute('data-bs-original-title')

        assert logged_in_as == "marcigranat@elte.hu"

@pytest.mark.asyncio
async def test_cookie_converter_marci():
    with tempfile.NamedTemporaryFile(suffix=".json") as temp_json:
        cookie_from_txt.convert_cookie_txt_to_json("cookies_raw/marcigranat.txt", temp_json.name)
        temp_json.flush()
        with open(temp_json.name, 'r') as f:
            cookie = json.loads(f.read())
    async with start_arcanum.arcanum_page(cookie=cookie) as page:
        await page.goto("https://adt.arcanum.com/hu/")
        logged_in_as = await page.locator('ul.navbar-nav.ms-auto.me-2 li.nav-item.dropdown a.btn.btn-outline-primary strong').get_attribute('data-bs-original-title')

        assert logged_in_as == "marcigranat@elte.hu"

@pytest.mark.asyncio
async def test_cookie_converter_petra():
    with tempfile.NamedTemporaryFile(suffix=".json") as temp_json:
        cookie_from_txt.convert_cookie_txt_to_json("cookies_raw/petratorok.txt", temp_json.name)
        temp_json.flush()
        with open(temp_json.name, 'r') as f:
            cookie = json.loads(f.read())
    async with start_arcanum.arcanum_page(cookie=cookie) as page:
        await page.goto("https://adt.arcanum.com/hu/")
        logged_in_as = await page.locator('ul.navbar-nav.ms-auto.me-2 li.nav-item.dropdown a.btn.btn-outline-primary strong').get_attribute('data-bs-original-title')
        time.sleep(6)
        assert logged_in_as == "F0D5F1@student.metropolitan.hu"
