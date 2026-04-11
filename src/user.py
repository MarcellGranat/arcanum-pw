from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import cycle
from pathlib import Path
from time import sleep
from typing import Iterator

import jsonlines
from pydantic import BaseModel

from .config import settings

LIMIT = 4800


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
    def download_logs(self) -> None | list[DownloadLog]:
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

    @property
    def limit_reached_at(self) -> datetime | None:
        if not self.download_log_path.exists():
            return None
        with jsonlines.open(self.download_log_path, "r") as reader:
            logs = [DownloadLog.model_validate_json(obj) for obj in reader]
        if not logs:
            return None
        latest = max(log.timestamp for log in logs)
        cutoff = latest - timedelta(hours=25)
        total = sum(log.n for log in logs if log.timestamp >= cutoff)
        if total > LIMIT:
            return latest
        return None


def get_users() -> list[User]:
    users = []
    for cookie_file in settings.cookie_folder.glob("*.json"):
        username = cookie_file.stem
        users.append(User(username=username))
    return users


@dataclass
class Exhausting:
    username: str
    exhausted_at: datetime


def next_user_cycle() -> Iterator[User]:
    users = get_users()
    if not users:
        raise RuntimeError("No users found in the cookie folder.")

    cycle_user = users[0]
    exhausted_times: list[Exhausting] = []
    for user in cycle(users):
        limit_reached_at = user.limit_reached_at
        if limit_reached_at is None or datetime.now() >= limit_reached_at + timedelta(
            hours=24
        ):
            cycle_user = user
            exhausted_times.clear()
            yield user
            continue
        else:
            exhausted_times.append(
                Exhausting(username=user.username, exhausted_at=limit_reached_at)
            )

        # end of circle
        if user == cycle_user:
            min_exhausted = min(exhausted_times, key=lambda x: x.exhausted_at)
            available_at: datetime = min_exhausted.exhausted_at + timedelta(hours=24)
            settings.logger.info(
                f"All users exhausted. Next available user: {min_exhausted.username} at {available_at.isoformat()}"
            )

            while datetime.now() < available_at:
                sleep(600)  # wait for 1 minute before checking again


def main() -> None:
    users = get_users()
    if not users:
        print("No users found in the cookie folder.")
        return

    for user in users:
        n = user.n_download_in24h
        limit_reached_at = user.limit_reached_at
        print(f"{user.username}: {n=}  {limit_reached_at=}")


if __name__ == "__main__":
    main()
