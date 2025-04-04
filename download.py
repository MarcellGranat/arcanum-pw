import re
import unidecode
import os
from loguru import logger
from datetime import datetime, timedelta
import aiofiles
import asyncio
import json
from log_download import log_download

logger.add("logs")

async def get_downloads_last_24h(username: str = "unknown") -> int:
    """Check the number of pages downloaded in the last 24 hours."""
    last_24h = datetime.now() - timedelta(days=1)
    count = 0

    async with aiofiles.open("download_log.json", "r", encoding="utf-8") as file:
        async for line in file:
            record = json.loads(line.strip())
            log_entry = eval(record["record"]["message"])
            if log_entry["user"] == username:
                timestamp = datetime.fromisoformat(log_entry["timestamp"])
                if timestamp >= last_24h:
                    count += log_entry["pages_downloaded"]

    return count

async def download_from_to(page, start: int, end: int, path: str) -> None:
    # type to the fields
    await asyncio.sleep(0.5) 
    await page.get_by_label("Oldalak mentése").get_by_role("button").click()
    await page.get_by_role("spinbutton", name="Mettől:").fill(str(start))
    await page.get_by_role("spinbutton", name="Meddig:").fill(str(end))

    # click the save button
    await asyncio.sleep(0.5)
    async with page.expect_download() as download_info:
        async with page.expect_popup() as page1_info:
            await page.get_by_role("button", name="Mentés").click()
            page1 = await page1_info.value
        download = await download_info.value

        for attempt in range(5): # try to save it 5 times
            try:
                await download.save_as(path)
                break 
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Failed to save file - {e}")
                await asyncio.sleep(2)  # Wait before retrying
            if attempt == 2:
                raise FileNotFoundError(f"Failed to save file after 5 attempts - {path}")
    await page1.close()

async def current_page(page):
    x = (
        await page.locator(
            'xpath=//*[contains(@class, "uiInputBase-input MuiInput-input MuiInputBase-inputAdornedEnd")]'
        )
        .nth(1)
        .get_attribute("value")
    )
    return int(x)


async def n_page(page):
    # Locate the element containing the total number of pages
    element = (
        await page.locator(
            'xpath=//*[contains(@class, "MuiInputAdornment-positionEnd")]'
        )
        .nth(1)
        .text_content()
    )

    # Extract the number from the text content
    total_pages = int(element.split("/")[1].strip())
    return total_pages


async def generate_blocks(
    page, include_header: bool = True, max_click: None | int = None
):
    """
    Generate blocks of pages by clicking on the tree items.

    Args:
      page: the page object
      include_header: whether to include the header block (first block might not start at page 1)
      max_click: the maximum number of clicks to perform (only for testing)
    """
    for attempt in range(3):
        try:
            buttons = await page.locator(
                'xpath=//*[contains(@class, "MuiTreeItem-label")]'
            ).all()
            if max_click is not None:
                buttons = buttons[:(max_click)]
                await buttons[0].click(timeout=2000)
            break
        except Exception as e:
            if attempt == 2:
                logger.warning(f"Failed to click for the next block - {e}")
                break
            await asyncio.sleep(1)
        

    block_start = await current_page(page)
    label = await buttons[0].text_content()
    if block_start != 1 and include_header:
        yield {"start": 1, "end": block_start - 1, "label": "header"}

    for button in buttons[1:]:
        await button.click()
        block_end = await current_page(page)
        yield {"start": block_start, "end": block_end - 1, "label": label}
        label = await button.text_content()
        block_start = block_end

    yield {"start": block_start, "end": await n_page(page), "label": label}


def split_by_limit(start: int, end: int, limit: int = 50):
    """
    Split the range [start, end] into smaller ranges of size limit (max download size is 50 pages)
    """
    for i in range(start, end, limit):
        yield i, min(i + limit - 1, end)


def tidy_filename(x: str = "temp.pdf"):
    eng_x = unidecode.unidecode(x)  # for hungarian characters é > e
    encoded = (
        "".join(c.lower() for c in eng_x if c.isalnum() or c == " " or c == "-")
        .replace(" ", "_")
        .encode("ascii", "ignore")
    )
    return re.sub(b"_+", b"_", encoded).decode("ascii").strip()


async def download_along_tree(
    page,
    folder: str = "temp",
    username: str = "unknown",
    include_header: bool = True,
    max_click: None | int = None,
    max_downloads: None | int = 50000 # TODO
):
    click_index = 0 # for testing

    async for block in generate_blocks(
        page, include_header=include_header, max_click=max_click
    ):
        i = 1 # 50 pages batch max > index in pdf filename
        for start, end in split_by_limit(block["start"], block["end"]):
            path = folder + "/" + tidy_filename(block["label"]) + "-" + str(i) + ".pdf"
            if os.path.exists(path):
                continue
            page_count = end - start + 1
            if max_downloads is not None and (await get_downloads_last_24h(username) + page_count) > max_downloads:
                print(f"Max downloads reached with {username}")
                break
            await download_from_to(page, start, end, path)
            await log_download(username, page_count, path)
            i += 1

        # * stop the process > only for testing
        click_index += + 1
        if (max_click) == click_index:
            break

async def download_along_batches(
    page,
    folder: str = "temp",
    username: str = "unknown",
    include_header: bool = True,
    max_batches: None | int = None,
    max_downloads: None | int = 5000
):
    i = 1 # 50 pages batch max > index in pdf filename
    for start, end in split_by_limit(1, n_page(page)):
        path = folder + "/" + "pdf_batch" + "-" + str(i) + ".pdf"

        page_count = end - start + 1
        if max_downloads is not None and await (get_downloads_last_24h(username) + page_count) > max_downloads:
            print("Max downloads reached with {username}")
            break

        if os.path.exists(path): # file is already downloaded
            print(f"{path} already exists")
            continue

        await download_from_to(page, start, end, path)
        await log_download(username, page_count, path)
        i += 1

        # * stop the process > only for testing
        if max_batches is not None and i > max_batches:
            break