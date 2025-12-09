from src.config import settings
from src.arcanum_page import page_with_cookie, ArcanumPage
from src.user import User
from src.panel_block import download_blocks
from src.download import download_from_to
from src.user import next_user_cycle
from typing import Iterable
from time import sleep

class UserExhaustedError(Exception):
    pass

def scape_arcanum_page(arcanum_page: ArcanumPage, user: User) -> None:
    if (arcanum_page.folder / "archivename.txt").exists():
        return
    
    with page_with_cookie(url=arcanum_page.url, cookie=user.cookie) as page:
        sleep(1)  # wait for the page to load
        for block in download_blocks(page):
            file = arcanum_page.folder / block.filename
            if file.exists():
                continue

            if user.n_download_in24h >= 4800:
                raise UserExhaustedError()
            download_from_to(page, block.start, block.end, file)
            user.add_download_log(block.count)
            sleep(2)
            # check downloaded file exists
            for _ in range(20):
                if file.exists():
                    break
                sleep(1)
            else:
                raise FileNotFoundError(f"Downloaded file not found: {file}")
            settings.logger.info(f"Downloaded {file} by user {user.username}")

    with open(arcanum_page.folder / "archivename.txt", "w") as f:
        f.write(arcanum_page.title)

def scrape_collection(pages: Iterable[ArcanumPage]) -> None:
    users = next_user_cycle()

    for arcanum_page in pages:
        settings.logger.info(f"Starting download for {arcanum_page.url}")
        while True:
            user = next(users)
            try:
                scape_arcanum_page(arcanum_page, user)
                break
            except UserExhaustedError:
                settings.logger.info(f"User {user.username} has exhausted their download quota. Trying next user.")
            except Exception as e:
                settings.logger.error(f"Error while downloading {arcanum_page.url} with user {user.username} - {e}")

def download_archive(landing_url: str) -> None:
    from .archive_links import generate_archive_decades, generate_archive_links
    for _, decade_link in generate_archive_decades(landing_url):
        arcanum_pages = generate_archive_links(decade_link)
        scrape_collection(arcanum_pages)

def main() -> None:
    download_archive("https://adt.arcanum.com/hu/collection/PestiHirlap/")
    
if __name__ == "__main__":
    settings.headless = False
    settings.slowmo = 300
    main()