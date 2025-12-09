import json
import os
from time import sleep
from src import settings
from playwright.sync_api import sync_playwright


def main():
    if not settings.cookie_folder.exists():
        settings.cookie_folder.mkdir(parents=True)

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://adt.arcanum.com/hu/accounts/login/?next=/hu/")

        for _ in range(60): # wait up to 3 minutes for manual login
            try:
                print("Checking login status...")
                username = page.locator(
                    "ul.navbar-nav.ms-auto.me-2 li.nav-item.dropdown a.btn.btn-outline-primary strong"
                ).get_attribute("data-bs-original-title", timeout=15000)
                if username:
                    print(f"Logged in as: {username}")
                    with open(settings.cookie_folder / f"{username}.json", "w") as f:
                        cookies = context.cookies()
                        f.write(json.dumps(cookies))
                    break
            except Exception:
                pass
            sleep(3)

    raise RuntimeError("Login timed out after 3 minutes.")

if __name__ == "__main__":
    main()