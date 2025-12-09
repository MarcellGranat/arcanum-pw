from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from itertools import cycle
from typing import Iterator
import jsonlines
from pydantic import BaseModel

from .config import settings


class DownloadLog(BaseModel):
    timestamp: datetime
    n: int

class User(BaseModel):
    username: str

    @property
    def cookie_path(self) -> Path:
        return settings.cookie_folder / f"{self.username}.json"
    
    @property
    def download_log_path(self) -> Path:
        return settings.download_log_folder / f"{self.username}.jsonl"
    
    @property
    def cookie(self) -> dict:
        with open(self.cookie_path, "r") as f:
            import json
            return json.load(f)
    
    @property
    def download_logs(self) -> None |list[DownloadLog]:
        if not self.download_log_path.exists():
            return
        logs = []
        with jsonlines.open(self.download_log_path, "r") as reader:
            for obj in reader:
                logs.append(DownloadLog.model_validate_json(obj))

    def add_download_log(self, n: int) -> None:
        log = DownloadLog(timestamp=datetime.now(), n=n)
        if not settings.download_log_folder.exists():
            settings.download_log_folder.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(self.download_log_path, "a") as writer:
            writer.write(log.model_dump_json())

    @property
    def n_download_in24h(self) -> int:
        logs = self.download_logs
        if not logs:
            return 0
        cutoff = datetime.now() - timedelta(hours=24)
        return sum(log.n for log in logs if log.timestamp >= cutoff)
    
def get_users() -> list[User]:
    users = []
    for cookie_file in settings.cookie_folder.glob("*.json"):
        username = cookie_file.stem
        users.append(User(username=username))
    return users

def next_user_cycle() -> Iterator[User]:
    users = get_users()
    if not users:
        raise RuntimeError("No users found in the cookie folder.")
    
    for user in cycle(users):
        if user.n_download_in24h < 4800:
            yield user

        if user == users[0]:
            for anyone in users:
                if anyone.n_download_in24h < 4800:
                    break
            else:
                settings.logger.info("All users have exhausted their download quota. Waiting for 24 hour.")
                sleep(24 * 3600)  # wait for 24 hours before retrying
                settings.logger.info("Retrying users after 24 hours.")