import start_arcanum
import asyncio
import download
import os
from manage_cookie import init_cookies, read_cookie
from loguru import logger
from process_manager import ProcessManager, hash_folder
import time

logger.add("logs")

waiting_for_limit = False

async def scrape_page_along_tree(username, archive: tuple[str, str]):
    folder = "data/" + download.tidy_filename(archive[0])
    if not os.path.exists(folder):
        os.makedirs(folder)

    # ! txt signals that the whole archive is downloaded
    if os.path.exists(f"{folder}/archivename.txt") and len(os.listdir(folder)) > 1: 
        logger.info(f"{archive[0]} already finished")
        return
    
    cookie = await read_cookie(username)

    async with start_arcanum.arcanum_page(cookie, headless=False) as page:
        logger.info(f"Going to {archive[1]} ({username})")
        while True:
            try:
                await page.goto(archive[1], timeout=30000)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to navigate to {archive[1]} ({username}): {e}")
            await asyncio.sleep(2)
            try:
                await download.download_along_tree(page, folder=folder, username=username)
            except Exception as e:
                logger.error(f"Failed to download {archive[0]} ({username}): {e}")
                continue
            logger.success(f"{archive[0]} finished")
            # ! write a single txt file in the folder > signal that the whole archive is downloaded
            with open(f"{folder}/archivename.txt", "w") as f:
                f.write(archive[0])
            break

def is_working():
    global waiting_for_limit
    if waiting_for_limit:
        time.sleep(3600 * 4)
        logger.info("Waiting for download limit to reset")
        waiting_for_limit = False
    return hash_folder(folder_path="data")

async def users():
    usernames = []

    cookies = await init_cookies(check=True, force=False)

    if not cookies:
        logger.error("No cookies found")
        raise Exception("No cookies found")

    for user in cookies:
        if await download.get_downloads_last_24h(user) > 4700:
            logger.info(f"User {user} has reached the download limit")
            continue
        if len(usernames) >= 2:
            break # Should use maximum 2 users at a time

        usernames.append(user)

    if not usernames:
        logger.error("No users with download limit available")
        asyncio.sleep(3600 * 10)
        global waiting_for_limit
        waiting_for_limit = True
        # TODO send notification

    return usernames

def main(items=None):
    process = ProcessManager(preprocess=users, func=scrape_page_along_tree, items=urls, check_function=is_working, timeout=300)
    asyncio.run(process.run())
    logger.success("All archives downloaded")

if __name__ == "__main__":
    import archive_links
    urls30s = list(archive_links.generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/?decade=1930#collection-contents"))
    urls20s = list(archive_links.generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/?decade=1920#collection-contents"))
    urls10s = list(archive_links.generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/?decade=1910#collection-contents"))
    urls = urls30s + urls20s + urls10s
    main(items=urls)