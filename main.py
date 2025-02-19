import parallel_execution
import start_arcanum
import asyncio
import download
import time
import os

async def download_archive(config, item):
    """Download the archive."""
    archive_name, archive_link = item
    print(f"Downloading {archive_name} from {archive_link}...")
    await start_arcanum.download_archive(config, archive_name, archive_link)
    return archive_name

async def scrape_page_along_tree(username, archive: tuple[str, str]):
    folder = "data/" + download.tidy_filename(archive[0])
        
    if not os.path.exists(folder):
        os.mkdir(folder)

    # ! txt signals that the whole archive is downloaded
    if os.path.exists(f"{folder}/archivename.txt") and len(os.listdir(folder)) > 1: 
        print(f"{folder} already exists")
        return
    
    cookie = start_arcanum.read_cookies(username)

    async with start_arcanum.arcanum_page(cookie, headless=False) as page:
        await page.goto(archive[1])
        time.sleep(2)
        await download.download_along_tree(page, folder=folder, username=username)

        # ! write a single txt file in the folder > signal that the whole archive is downloaded
        with open(f"{folder}/archivename.txt", "w") as f:
            f.write(archive[0])


async def parallel_scrape_page_along_tree(tuples_list):
    usernames = []
    if not os.path.exists("data"):
        os.mkdir("data")

    for user in start_arcanum.generate_usernames():
        # if await download.get_downloads_last_24h(user) < 4900:
        usernames.append(user)
    
    await parallel_execution.parallel_exec(func=scrape_page_along_tree, configs=usernames, items=tuples_list)

if __name__ == "__main__":
    import archive_links
    urls = list(archive_links.generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/?decade=1870#collection-contents"))
    asyncio.run(parallel_scrape_page_along_tree(tuples_list=urls))