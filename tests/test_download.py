from start_arcanum import arcanum_page, generate_usernames, read_cookies
from download import download_from_to, current_page, n_page, generate_blocks
from download import split_by_limit, tidy_filename, download_along_tree
from download import log_download, get_downloads_last_24h
import pytest
import tempfile
from pypdf import PdfReader
import glob
import os
import time

cookie = read_cookies(next(generate_usernames()))

@pytest.mark.asyncio
async def test_download():
    async with arcanum_page(cookie=cookie, headless=True) as page:
        await page.goto(
            "https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/?pg=10&layout=s"
        )

        assert await current_page(page) == 11

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
            await download_from_to(page, 1, 1, temp_pdf.name)
            temp_pdf.seek(0)

            # Check the number of pages in the downloaded PDF
            pdf_reader = PdfReader(temp_pdf)
            num_pages = len(pdf_reader.pages)
            assert num_pages == 1, f"Expected 1 page, but got {num_pages}"


@pytest.mark.asyncio
async def test_n_page():
    async with arcanum_page(cookie=cookie) as page:
        await page.goto("https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/")
        assert await n_page(page) == 446


@pytest.mark.asyncio
async def test_block_generator():
    async with arcanum_page(cookie=cookie) as page:
        await page.goto("https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/")
        blocks = []
        async for block in generate_blocks(page, max_click=4):
            blocks.append(block)
        assert blocks == [
            {"start": 1, "end": 2, "label": "header"},
            {"start": 3, "end": 10, "label": "1841-01-02 / 1. szám"},
            {"start": 11, "end": 18, "label": "1841-01-06 / 2. szám"},
            {"start": 19, "end": 26, "label": "1841-01-09 / 3. szám"},
            {"start": 27, "end": 446, "label": "1841-01-13 / 4. szám"},
        ]


def test_split_by_limit():
    assert next(split_by_limit(1, 10)) == (1, 10)

    splits = split_by_limit(14, 88)
    assert next(splits) == (14, 63)
    assert next(splits) == (64, 88)


def test_tidy_filename():
    assert tidy_filename("Nemzeti Sport") == "nemzeti_sport"
    assert tidy_filename("Áéőá 23") == "aeoa_23"
    assert tidy_filename("Spaces / double") == "spaces_double"


@pytest.mark.asyncio
async def test_download_along_tree():
    with tempfile.TemporaryDirectory() as temp_dir:
        username = next(generate_usernames())
        async with arcanum_page(cookie=read_cookies(username)) as page:
            await page.goto("https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/")
            time.sleep(0.05)
            await download_along_tree(
                page, folder=temp_dir, username=username, max_click=3
            )

            # Get list of PDF files in temp_dir
            pdf_files = sorted(glob.glob(os.path.join(temp_dir, "*.pdf")))
            assert len(pdf_files) == 3  # Header + first 2 issues
            assert os.path.basename(pdf_files[0]) == "1841-01-02_1_szam-1.pdf"

            assert len(PdfReader(pdf_files[0]).pages) == 8


@pytest.mark.asyncio
async def test_headless_mode():
    with tempfile.TemporaryDirectory() as temp_dir:
        username = next(generate_usernames())
        async with arcanum_page(cookie=cookie, headless=True, slow_mo=1000) as page:
            await page.goto("https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/")
            time.sleep(2)
            await download_along_tree(
                page, folder=temp_dir, username=username, max_click=3
            )

            # Get list of PDF files in temp_dir
            pdf_files = sorted(glob.glob(os.path.join(temp_dir, "*.pdf")))
            assert len(pdf_files) == 3  # Header + first 2 issues
            assert os.path.basename(pdf_files[0]) == "1841-01-02_1_szam-1.pdf"

            assert len(PdfReader(pdf_files[0]).pages) == 8


@pytest.mark.asyncio
async def test_download_log():
    downloads_pre = await get_downloads_last_24h("random goat")
    await log_download("random goat", 2, "test.pdf")
    downloads_post = await get_downloads_last_24h("random goat")
    assert downloads_post - downloads_pre == 2

@pytest.mark.asyncio
async def test_max_pages():
    username = next(generate_usernames())
    downloads_pre = await get_downloads_last_24h(username)
    with tempfile.TemporaryDirectory() as temp_dir:
        username = next(generate_usernames())
        cookie = read_cookies(username)
        async with arcanum_page(cookie=cookie, headless=True) as page:
            await page.goto("https://adt.arcanum.com/hu/view/PestiHirlap_1841-1/")
            time.sleep(2)
            await download_along_tree(
                page, folder=temp_dir, username=username, max_click=5, max_downloads = downloads_pre + 20
            )

            # Get list of PDF files in temp_dir
            pdf_files = sorted(glob.glob(os.path.join(temp_dir, "*.pdf")))
            assert len(pdf_files) == 3  # ! stop before 20 pages
            