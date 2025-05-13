from loguru import logger
from datetime import datetime

logger.add(
    "download_log.json", 
    serialize=True, 
    enqueue=True, 
    level="INFO", 
    filter=lambda record: record["module"] == "log_download",
    rotation="1 week",
)

async def log_download(username: str = "unknown", page_count: int = 0, path: str = "") -> None:
    """Log the number of pages downloaded by a user."""
    logger.info({"user": username, "pages_downloaded": page_count, "timestamp": datetime.now().isoformat(), "path": path})