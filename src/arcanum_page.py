from contextlib import contextmanager
from pathlib import Path
import unidecode
from playwright.sync_api import sync_playwright
import re
from .config import settings
from .user import get_users
from pydantic import BaseModel


def default_user_cookie() -> dict:
    for user in get_users():
        if user.n_download_in24h < 5000:
            return user.cookie
    raise RuntimeError("No user with available download quota.")


example_arcanum_site = (
    "https://adt.arcanum.com/hu/view/PestiHirlap_1879_01/?pg=28&layout=s"
)

def tidy_filename(x: str = "temp.pdf"):
    eng_x = unidecode.unidecode(x)  # for hungarian characters é > e
    encoded = (
        "".join(c.lower() for c in eng_x if c.isalnum() or c == " " or c == "-")
        .replace(" ", "_")
        .encode("ascii", "ignore")
    )
    return re.sub(b"_+", b"_", encoded).decode("ascii").strip()

@contextmanager
def page_with_cookie(
    url: str = example_arcanum_site, cookie: dict = default_user_cookie()
):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=settings.headless, slow_mo=settings.slowmo
        )
        context = browser.new_context()

        # add cookie before navigating
        context.add_cookies(cookie)

        page = context.new_page()
        page.goto(url)

        try:
            yield page
        finally:
            context.close()
            browser.close()

class ArcanumPage(BaseModel):
    title: str
    url: str

    @property
    def folder(self) -> Path:
        return settings.data_folder / tidy_filename(self.title)
