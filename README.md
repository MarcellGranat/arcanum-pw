# README

Arcanum-PW is a Python project designed to run a scraping process with multiple users at the same time. It uses Playwright to scrape data from a website and save it to a local folder.

> [!CAUTION]
> Significant changes have been made recently. Please refer to the updated README and documentation for the latest usage instructions.

## Features

- Runs a scraping process with multiple cookies in sync mode (since the last change).
- Stops the process gracefully when the data limit is reached.

## Installation

```
uv sync
uv run playwright install
```

## Usage

To use this project with one or more users, you need their cookies in the `cookies/` folder. This can be done using the login tools

```
python -m src.login_tool
```

**Once you are logged in with any user in the popup browser, the cookie will be saved in the `cookies/` folder.**

To start the scraping process, run:

```
python -m tools.scrape
```

You will be prompted to enter the Arcanum collection landing page URL (e.g.: https://adt.arcanum.com/hu/collection/PestiHirlap/). The scraper will then start downloading the data using the cookies provided.