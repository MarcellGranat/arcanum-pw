import os
import json
from playwright.async_api import async_playwright
import asyncio
import time

def generate_usernames():
  for file in os.listdir("cookies"):
    yield file.removesuffix(".json")

def read_cookies(username):
  with open("cookies/" + username + ".json", "r") as f:
    return json.loads(f.read())

def generate_cookies():
  for username in generate_usernames():
      yield read_cookies(username)

class arcanum_page(object):
    def __init__(self, cookie=None, headless=False, slow_mo: int | None = 500):
        self.cookie = cookie
        self.headless = headless
        self.slow_mo = slow_mo

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(
            headless=self.headless, slow_mo=self.slow_mo
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        if self.cookie:
            await self.context.add_cookies(self.cookie)
        return self.page

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()

async def main():
    user_cookies = generate_cookies()
    async with arcanum_page(headless=True, cookie=next(user_cookies)) as page:
        await page.goto("https://adt.arcanum.com/en/discover/")
        time.sleep(2)
        await page.screenshot(path="test.png")

    async with arcanum_page(headless=True, cookie=next(user_cookies)) as page:
        await page.goto("https://adt.arcanum.com/en/discover/")
        time.sleep(2)
        await page.screenshot(path="test2.png")

    async with arcanum_page(headless=True, cookie=next(user_cookies)) as page:
        await page.goto("https://adt.arcanum.com/en/discover/")
        time.sleep(2)
        await page.screenshot(path="test3.png")


if __name__ == "__main__":
    asyncio.run(main())

