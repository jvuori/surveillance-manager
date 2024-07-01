from pathlib import Path
import sqlite3
import hashlib
from datetime import datetime
from survin.models import Status, Video


def _get_db() -> sqlite3.Connection:
    return sqlite3.connect("survin.db")


def create_db():
    db = _get_db()
    db.execute(
        """CREATE TABLE IF NOT EXISTS videos (
            guid TEXT PRIMARY KEY,
            source TEXT,
            timestamp TEXT,
            video_path TEXT,
            status TEXT
        )"""
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_status ON videos (status)")
    db.execute(
        "CREATE TABLE IF NOT EXISTS classifications (video_path TEXT, classification TEXT)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_classification_path ON classifications (video_path)"
    )
    db.commit()


def add_video(video_path: Path, source: str, timestamp: datetime) -> str:
    guid = hashlib.md5(str(video_path).encode()).hexdigest()
    db = _get_db()
    db.execute(
        "INSERT INTO videos (guid, source, timestamp, video_path, status) VALUES (?, ?, ?, ?, ?)",
        (guid, source, timestamp.isoformat(), str(video_path), Status.NEW.name),
    )
    db.commit()
    return guid


def get_video_path(guid: str) -> Path | None:
    db = _get_db()
    row = db.execute("SELECT video_path FROM videos WHERE guid = ?", (guid,)).fetchone()
    return Path(row[0]) if row else None


def set_classifications(video_path: Path, classifications: set[str]):
    db = _get_db()
    for classification in classifications:
        db.execute(
            "INSERT INTO classifications (video_path, classification) VALUES (?, ?)",
            (str(video_path), classification),
        )
    db.commit()


def get_classifications(video_path: Path) -> set[str]:
    db = _get_db()
    return {
        row[0]
        for row in db.execute(
            "SELECT classification FROM classifications WHERE video_path = ?",
            (str(video_path),),
        )
    }


def set_status(video_path: Path, status: Status):
    db = _get_db()
    db.execute(
        "UPDATE videos SET status = ? WHERE video_path = ?",
        (status.name, str(video_path)),
    )
    db.commit()


def get_video_paths_by_status(status: Status) -> list[Path]:
    db = _get_db()
    return [
        Path(row[0])
        for row in db.execute(
            "SELECT video_path FROM videos WHERE status = ?", (status.name,)
        )
    ]


def get_videos_by_status(status: Status) -> list[Video]:
    db = _get_db()
    return [
        Video(
            guid=row[0],
            file_path=row[1],
            status=Status[row[2]],
            classifications=get_classifications(Path(row[1])),
            timestamp=row[3],
        )
        for row in db.execute(
            "SELECT guid, video_path, status, timestamp FROM videos WHERE status = ?",
            (status.name,),
        )
    ]


def get_status(video_path: Path) -> Status | None:
    db = _get_db()
    row = db.execute(
        "SELECT status FROM videos WHERE video_path = ?", (str(video_path),)
    ).fetchone()
    return Status[row[0]] if row else None
