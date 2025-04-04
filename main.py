import start_arcanum
import asyncio
import download
import os
from manage_cookie import init_cookies, read_cookie
from loguru import logger
from process_manager import ProcessManager
from hashing import hash_file
from pypushover import notify_after_elapsed_time, send_message
from limit import limit_reached


logger.add("logs")


async def scrape_page_along_tree(username, archive: tuple[str, str]):
    folder = "data/" + download.tidy_filename(archive[0])
    if not os.path.exists(folder):
        os.makedirs(folder)

    # ! txt signals that the whole archive is downloaded
    # if os.path.exists(f"{folder}/archivename.txt") and len(os.listdir(folder)) > 1:
    #     logger.info(f"{archive[0]} already finished")
    #     return

    cookie = await read_cookie(username)

    async with start_arcanum.arcanum_page(cookie, headless=True) as page:
        logger.info(f"Going to {archive[1]} ({username})")
        while True:
            try:
                await page.goto(archive[1], timeout=30000)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to navigate to {archive[1]} ({username}): {e}")
            await asyncio.sleep(2)
            try:
                await download.download_along_tree(
                    page, folder=folder, username=username
                )
            except Exception as e:
                logger.error(f"Failed to download {archive[0]} ({username}): {e}")
                continue
            logger.success(f"{archive[0]} finished")
            # ! write a single txt file in the folder > signal that the whole archive is downloaded
            with open(f"{folder}/archivename.txt", "w") as f:
                f.write(archive[0])
            break


download_hash = hash_file("download_log.json")


async def process_stopped() -> bool:
    global download_hash
    new_hash = hash_file("download_log.json")

    if new_hash != download_hash:
        download_hash = new_hash
        notify_after_elapsed_time(
            "Still scraping", title="Arcanum", elapsed_time=3600 * 6, init=True
        )
        return False
    return True


users = None


async def pick_users(users: list[str], n: int = 2) -> list[str]:
    picked = []
    for user in users:
        if not await limit_reached(user):
            logger.info(f"User {user} is available")
            picked.append(user)
        if len(picked) >= n:
            return picked

    return picked if picked else None


async def preprocess():
    global users
    current_users = await pick_users(users)
    while not current_users:
        if current_users:
            return current_users
        else:
            logger.info("No users available")
            await asyncio.sleep(3600)
            current_users = await pick_users(users)
    return current_users


def main(items=None):
    global users
    users = asyncio.run(init_cookies(check=True, force=False))

    process = ProcessManager(
        preprocess=preprocess,
        func=scrape_page_along_tree,
        items=urls,
        check_function=process_stopped,
        timeout=600,
    )
    asyncio.run(process.run())
    logger.success("All archives downloaded")
    send_message("All archives downloaded", title="Arcanum")


if __name__ == "__main__":
    import archive_links

    urls = []
    decades = archive_links.generate_archive_decades("https://adt.arcanum.com/hu/collection/PestiHirlap/")
    for decade_name, decade_link in decades:
        print(decade_link)
        urls.extend(list(archive_links.generate_archive_links(decade_link)))

    main(items=urls)
