from playwright.sync_api import sync_playwright
import json
import os

with open(".arcanum_secrets", "r") as f:
    userdata = f.read().split("\n")

users = []
for i in range(len(userdata) // 4 + 1):
    users.append({
        "uni": userdata[i * 4].strip(),
        "username": userdata[i * 4 + 1].strip(),
        "password": userdata[i * 4 + 2].strip()
    })

pw = sync_playwright().start()

for user in users:
    browser = pw.firefox.launch(
        headless=False, slow_mo=1000
    )

    context = browser.new_context()
    page = context.new_page()

    page.goto("https://adt.arcanum.com/hu/accounts/login/?next=/hu/")

    # closing cookies
    page.get_by_text("Allow all").click()

    # login with eduID
    page.locator("xpath=//a[contains(@href, 'shibsession/')]").click()

    # arrow for searching
    page.locator('xpath=//*[@id="userInputArea"]/div[1]/span/span[1]/span/span[2]').click()

    # type your uni
    page.get_by_role("searchbox").fill(user["uni"])
    page.get_by_role("searchbox").press("Enter")
    page.get_by_role("button").get_by_text("Select").click()

    page.get_by_role("textbox").nth(0).fill(user["username"])
    page.get_by_role("textbox").nth(1).fill(user["password"])
    page.get_by_role("button").click()
    page.screenshot(path="login.png")

    # TODO save cookies
    user_hash = hash(user["username"] + user["password"])
    os.mkdir("cookies")
    with open("cookies/" + str(user_hash) + ".json", "w") as f:
        f.write(json.dumps(context.cookies()))
    
    browser.close()