import os
import json
import asyncio
import aiofiles
from playwright.async_api import async_playwright
from loguru import logger
import time

cookie_folder = "cookies/"

logger.add("logs")

def set_cookie_folder(folder):
    global cookie_folder
    cookie_folder = folder

async def read_cookie(username):
    global cookie_folder
    async with aiofiles.open(cookie_folder + username + ".json", "r") as f:
        return json.loads(await f.read())

async def logged_in_as(cookie):
    try:
        async with async_playwright() as pw:
            browser = await pw.firefox.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            if cookie:
                await context.add_cookies(cookie)
            await page.goto("https://adt.arcanum.com/hu/")
            await asyncio.sleep(0.5)
            username = await page.locator(
                "ul.navbar-nav.ms-auto.me-2 li.nav-item.dropdown a.btn.btn-outline-primary strong"
            ).get_attribute("data-bs-original-title", timeout=15000)
            
            await browser.close()
            
            if username:
                return username
            raise Exception("Username not found")
    except Exception as e:
        raise ValueError("Cookie is invalid or expired") from e

async def cookie_from_password(username, password, uni="Budapest Metropolitan University", headless=False, slow_mo=1000, save=True):
    global cookie_folder
    async with async_playwright() as pw:
        browser = await pw.firefox.launch(headless=headless, slow_mo=slow_mo)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://adt.arcanum.com/hu/accounts/login/?next=/hu/")
        await asyncio.sleep(2)
        await page.get_by_text("Allow all").click()  # closing cookies
        
        if uni:
            await page.locator("xpath=//a[contains(@href, 'shibsession/')]").click()
            await page.locator('xpath=//*[@id="userInputArea"]/div[1]/span/span[1]/span/span[2]').click()
            await page.get_by_role("searchbox").fill(uni)
            await page.get_by_role("searchbox").press("Enter")
            await page.get_by_role("button").get_by_text("Select").click()
        else:
            raise NotImplementedError("Only eduID login is supported")
        
        await page.get_by_role("textbox").nth(0).fill(username)
        await page.get_by_role("textbox").nth(1).fill(password)
        await page.get_by_role("button").click()
        
        if not os.path.exists(cookie_folder):
            os.mkdir(cookie_folder)
        
        filename = username.replace("@", "_").removesuffix(".hu")
        cookies = await context.cookies()
        
        if save:
            logger.info(f"Saving cookie for {username} to {cookie_folder}/{filename}.json")
            async with aiofiles.open(cookie_folder + filename + ".json", "w") as f:
                await f.write(json.dumps(cookies))
        
        await browser.close()
        
        return cookies
    
async def cookie_from_txt(txt_path: str, save=True):
    global cookie_folder

    async with aiofiles.open(txt_path) as file:
        item_names = [
            "name",
            "value",
            "domain",
            "path",
            "expires",
            "httpOnly",
            "secure",
            "sameSite",
        ]

        list_of_cookies = []
        lines = (await file.read()).splitlines()
        for line in lines:
            cookie_item = {}
            values = line.split("\t")
            for name, value in zip(item_names, values):
                cookie_item[name] = value.strip()

            # Convert expires to timestamp if necessary
            if "expires" in cookie_item and cookie_item["expires"]:
                try:
                    cookie_item["expires"] = int(
                        time.mktime(
                            time.strptime(
                                cookie_item["expires"], "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                        )
                    )
                except ValueError:
                    pass

            # Convert httpOnly and secure to boolean
            cookie_item["httpOnly"] = cookie_item["httpOnly"] == "✓"
            cookie_item["secure"] = cookie_item["secure"] == "✓"

            # Ensure sameSite is one of the expected values
            if cookie_item["sameSite"] not in ["Strict", "Lax", "None"]:
                cookie_item["sameSite"] = "None"

            list_of_cookies.append(cookie_item)

    username = await logged_in_as(list_of_cookies)
    filename = username.replace("@", "_").removesuffix(".hu")
    if save:
        logger.info(f"Saving cookie for {username} to {cookie_folder}/{filename}.json")
        async with aiofiles.open(cookie_folder + filename + ".json", "w") as file:
            await file.write(json.dumps(list_of_cookies, indent=4))
    return list_of_cookies


async def ativate_cookies_from_txt(txt_folder):
    global cookie_folder
    txt_files = os.listdir(txt_folder)
    for txt_file in txt_files:
        await cookie_from_txt(txt_folder + txt_file, cookie_folder)


async def activate_cookies_from_password(
    secret_file=".arcanum_secrets", headless=False, slow_mo=1000
):
    global cookie_folder
    async with aiofiles.open(".arcanum_secrets", "r") as f:
        userdata = (await f.read()).split("\n")

    users = []
    for i in range(len(userdata) // 4 + 1):
        users.append(
            {
                "uni": userdata[i * 4].strip(),
                "username": userdata[i * 4 + 1].strip(),
                "password": userdata[i * 4 + 2].strip(),
            }
        )

    for user in users:
        await cookie_from_password(
            user["username"],
            user["password"],
            user["uni"],
            headless,
            slow_mo,
            save=True,
        )

async def generate_usernames():
    global cookie_folder
    for file in os.listdir(cookie_folder):
        yield file.removesuffix(".json")

async def init_cookies(cookie_folder="cookies/", secret_file=".arcanum_secrets", txt_folder="txt_cookies/", check=True, force=False, headless=True, slow_mo=1000):
    logger.info("Initializing cookies")

    if not os.path.exists(cookie_folder):
        os.mkdir(cookie_folder)
        force = True
    
    set_cookie_folder(cookie_folder)
    
    if force:
        if os.path.exists(txt_folder):
            await ativate_cookies_from_txt(txt_folder)
        if os.path.exists(secret_file):
            await activate_cookies_from_password(secret_file, headless, slow_mo)

    failed_any = False
    valid_cookie_files = []
    
    async for filename in generate_usernames():
        try:
            cookie = await read_cookie(filename)
            username = await logged_in_as(cookie)
            valid_cookie_files.append(filename)
            logger.info(f"Cookie for {username} is valid")
        except ValueError:
            logger.error(f"Cookie for {filename} is invalid")
            if check:
                failed_any = True
                os.remove(cookie_folder + filename + ".json")
    
    if failed_any:
        logger.info("Some cookies were invalid. Relogging from credentials")
        await activate_cookies_from_password(secret_file, headless, slow_mo)
        valid_cookie_files = []
        
        async for filename in generate_usernames():
            try:
                cookie = await read_cookie(filename)
                username = await logged_in_as(cookie)
                valid_cookie_files.append(filename)
                logger.info(f"Cookie for {username} is valid")
            except ValueError:
                logger.error(f"Cookie for {filename} is invalid")
    
    if not valid_cookie_files:
        logger.error(f"No valid cookies in folder {cookie_folder}")
    
    return valid_cookie_files

if __name__ == "__main__":
    asyncio.run(init_cookies(force=True, check=True, txt_folder="cookies_raw/"))
