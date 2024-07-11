from pathlib import Path
from datetime import datetime
from survin import __main__


def test_get_timestamp_from_file_name():
    file_path = Path("TERASSI___2024-06-30___00-08-38")
    assert __main__._get_timestamp_from_file_name(file_path) == datetime(
        2024, 6, 30, 0, 8, 38
    )


def test_save_snapshot_picture_from_video():
    file_path = Path(__file__).parent.joinpath("videos/police.mkv")
    snapshot_path = Path(__file__).parent.joinpath("snapshots/police.jpg")
    __main__._save_snapshot_picture_from_video(file_path, snapshot_path)
