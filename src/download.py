from playwright.sync_api import Page
from time import sleep
from .config import settings
from .panel_block import Block
from pathlib import Path

def download_from_to(page: Page, start: int, end: int, path: Path) -> None:
    # type to the fields
    page.get_by_label("Oldalak mentése").get_by_role("button").click()
    page.get_by_role("spinbutton", name="Mettől:").fill(str(start))
    page.get_by_role("spinbutton", name="Meddig:").fill(str(end))

    # click the save button
    sleep(0.5)  # wait for the button to be enabled
    with page.expect_download() as download_info:
        with page.expect_popup() as page1_info:
            page.get_by_role("button", name="Mentés").click()
            page1 = page1_info.value
        download = download_info.value

        for attempt in range(5): # try to save it 5 times
            try:
                download.save_as(path)
                break 
            except Exception as e:
                settings.logger.warning(f"Attempt {attempt + 1}: Failed to save file - {e}")
                sleep(2)  # Wait before retrying
            if attempt == 2:
                raise FileNotFoundError(f"Failed to save file after 2 attempts - {path}")
    page1.close()
