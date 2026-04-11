from pathlib import Path

from src.__main__ import main
from src.config import settings


def test_workflow(tmp_path: Path) -> None:
    settings.data_folder = tmp_path / "data"
    main()
