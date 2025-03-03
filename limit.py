from download import get_downloads_last_24h
from loguru import logger
from datetime import datetime, timedelta
import aiofiles
import json

logger.add(
    "log_limit.json",
    serialize=True,
    enqueue=True,
    level="INFO",
    filter=lambda record: record["module"] == "limit",
)


async def log_exceeded(username: str = "unknown") -> None:
    """Log the number of pages downloaded by a user."""
    logger.info({"user": username, "timestamp": datetime.now().isoformat()})


async def over_based_download_log(username: str = "unknown") -> bool:
    if await get_downloads_last_24h(username) > 4700:
        return True
    else:
        return False


async def get_last_limit_reach_time(username: str = "unknown") -> datetime:
    timestamp = None
    async with aiofiles.open("log_limit.json", "r", encoding="utf-8") as file:
        async for line in file:
            record = json.loads(line.strip())
            log_entry = eval(record["record"]["message"])
            if log_entry["user"] == username:
                timestamp = datetime.fromisoformat(log_entry["timestamp"])
        if timestamp:
            return timestamp


async def limit_reached(username: str = "unknown", timeout: int = 3600 * 22) -> bool:
    """Check if the download limit has been reached."""
    limit_reached_time = await get_last_limit_reach_time(username)

    if limit_reached_time:
        if limit_reached_time > datetime.now() - timedelta(seconds=timeout):
            return True

    if await over_based_download_log(username):
        await log_exceeded(username)
        return True

    return False
