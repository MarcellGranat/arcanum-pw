# Arcanum-PW

Arcanum-PW is a Python project designed to run a scraping process with multiple users at the same time. It uses Playwright to scrape data from a website and save it to a local folder.

## Features

- Runs a scraping process with multiple cookies simultaneously.
- Stops the process gracefully when the data limit is reached.

## Requirements

- Python >= 3.13
- Playwright >= 1.15.0


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/arcanum-pw.git
    cd arcanum-pw
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install uv
    uv pip install -r requirements.txt
    ```

## Usage


### Parallel Execution

The project supports running a scraping process with multiple cookies simultaneously.

### Running the Script

To run the script with your settings, follow these steps:

1. Set your login cookies by creating JSON files in the `cookies/` folder. The JSON files should have the following structure.

(You can use the `cookies_from_txt.py` script to convert browser cookies to the required JSON format or `save_cookies.py` to save cookies from a username and password.)

Example json files:

```json
{
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": "cookie_domain",
    "path": "cookie_path",
    "expires": "cookie_expires",
    "httpOnly": "cookie_httpOnly",
    "secure": "cookie_secure",
    "sameSite": "cookie_sameSite"
}
```

2. Modify and run the `main.py` script.

The script will start the scraping process using multiple cookies.

### Running Tests

To run the tests, use the following command:

```sh
pytest
```

(Some tests are based on cookies, that are not included in the public repository.)
