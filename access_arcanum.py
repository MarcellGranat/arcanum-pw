import os
import json
from playwright.sync_api import sync_playwright

def user_cookies():
  user_files = os.listdir("cookies")
  for file in user_files:
    with open("cookies/" + file, "r") as f:
      cookies = json.loads(f.read())
      yield cookies

for cookies in user_cookies():
  with sync_playwright() as p:
    browser = p.firefox.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    page.goto("https://adt.arcanum.com/hu/")
    page.screenshot(path="arcanum.png")
