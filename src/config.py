from pathlib import Path
from loguru import logger
from pydantic_settings import BaseSettings
from typing import Any

class Settings(BaseSettings):
    cookie_folder: Path = Path("cookies")
    data_folder: Path = Path("data")
    headless: bool = False
    slowmo: float = 200

    download_log_folder: Path = Path("download_logs")
    logger: Any = logger

settings = Settings()
settings.logger.add(".log", rotation="10 MB")