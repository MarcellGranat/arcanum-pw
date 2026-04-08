from time import sleep
from typing import Iterator

from playwright.sync_api import Page
from pydantic import BaseModel

from .arcanum_page import tidy_filename
from .config import settings


class Block(BaseModel):
    start: int
    end: int
    label: str
    index: int | None = None

    @property
    def filename(self) -> str:
        if self.index is None:
            raise ValueError("Index is not set for this block.")
        return tidy_filename(f"{self.label}-{self.index}") + ".pdf"

    @property
    def count(self) -> int:
        return self.end - self.start + 1


def current_page(page: Page) -> int:
    button = page.locator("[class*='MuiInputBase-inputAdornedEnd']")
    number = button.get_attribute("value")
    if number:
        return int(number)
    else:
        raise RuntimeError("Could not determine current page number.")


def max_page(page: Page) -> int:
    button = page.locator(
        "[class*='MuiInputAdornment-root MuiInputAdornment-positionEnd']"
    )
    value = button.text_content()
    if value:
        number_part = value.removeprefix("/ ")
        return int(number_part)
    else:
        raise RuntimeError("Could not determine maximum page number.")


def block_buttons(page: Page):
    tabpanel = page.get_by_role("tabpanel")
    buttons = tabpanel.get_by_role("treeitem")
    return buttons


def blocks(page: Page, include_header: bool = True) -> Iterator[Block]:
    """
    Generate blocks of pages by clicking on the tree items.

    Args:
        page: the page object
        include_header: whether to include the header block (first block might not start at page 1)
    """
    buttons = None

    for attempt in range(3):
        try:
            page.get_by_role("tab").nth(1).click()
            sleep(1)
            tabpanel = page.get_by_role("tabpanel")
            buttons = tabpanel.get_by_role("treeitem")
            if not buttons.count():
                raise RuntimeError("No block buttons found.")
            buttons.nth(0).click(timeout=2000)
            break
        except Exception as e:
            if attempt == 2:
                settings.logger.warning(f"Failed to click for the next block - {e}")
                break

        sleep(1)

    if not buttons:
        raise RuntimeError("No block buttons found after retries.")

    button_count = buttons.count()

    block_start = current_page(page)
    label = buttons.nth(0).text_content()
    if block_start != 1 and include_header:
        yield Block(start=1, end=block_start - 1, label="header")

    for i in range(1, button_count):
        button = buttons.nth(i)
        button.click()
        block_end = current_page(page)
        yield Block(start=block_start, end=block_end - 1, label=label)
        label = button.text_content()
        block_start = block_end

    yield Block(start=block_start, end=max_page(page), label=label)


def download_blocks(page: Page, include_header: bool = True) -> Iterator[Block]:
    for block in blocks(page, include_header=include_header):
        start = block.start
        for i in range(1, 100):
            end = min(start + 49, block.end)
            yield Block(start=start, end=end, label=block.label, index=i)
            if end == block.end:
                break
            start = end + 1
