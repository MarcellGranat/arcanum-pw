from src.arcanum_page import page_with_cookie
from src.config import settings
from src.panel_block import blocks
from time import sleep
from pathlib import Path

settings.headless = False

def test_page_numbers():
    with page_with_cookie() as page:
        assert page.url.startswith("https://adt.arcanum.com/hu/view/")
            
        init = True
        block_end = None

        for block in blocks(page):
            sleep(2)
            block_start = block.start
            if init:
                assert block_start == 1
                init = False
            else:
                if not block_end is None:
                    assert block_start == block_end + 1
            block_end = block.end
            init = False

def test_download():
    from src.download import download_from_to
    from tempfile import TemporaryDirectory

    with page_with_cookie() as page:
        sleep(2)
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"
            download_from_to(page, 1, 3, path)
            assert path.exists()
        