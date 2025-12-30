import os
import time
import pytest

from pathlib import Path

from src.configs.functions import get_latest_file_in_folder, move_file_to_folder


def test_get_latest_file_in_folder_picks_most_recent(tmp_path: Path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"

    f1.write_text("x")
    time.sleep(0.01)  # ensure mtime differs on fast FS
    f2.write_text("y")

    latest = get_latest_file_in_folder(str(tmp_path), "*.csv")
    assert os.path.basename(latest) == "b.csv"


def test_get_latest_file_in_folder_raises_when_none(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        get_latest_file_in_folder(str(tmp_path), "*.csv")


def test_move_file_to_folder_moves_file(tmp_path: Path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()

    src_file = src_dir / "x.csv"
    src_file.write_text("hello")

    moved_path = move_file_to_folder(str(src_file), str(dst_dir))

    assert os.path.exists(moved_path)
    assert os.path.basename(moved_path) == "x.csv"
    assert not src_file.exists()
