from pathlib import Path
import sqlite3
import hashlib
from datetime import datetime, date, time
from survin.models import Status, Video


def _get_db() -> sqlite3.Connection:
    return sqlite3.connect("survin.db")


def create_db():
    db = _get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            guid TEXT PRIMARY KEY,
            source TEXT,
            date TEXT,
            time TEXT,
            video_path TEXT,
            status TEXT
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_status ON videos (status)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_date ON videos (date)")

    db.execute(
        "CREATE TABLE IF NOT EXISTS classifications (video_path TEXT, classification TEXT)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_classification_path ON classifications (video_path)"
    )
    db.commit()


def add_video(video_path: Path, source: str, video_date: date, video_time: time) -> str:
    guid = hashlib.md5(str(video_path).encode()).hexdigest()
    db = _get_db()
    db.execute(
        "INSERT INTO videos (guid, source, date, time, video_path, status) VALUES (?, ?, ?, ?, ?, ?)",
        (
            guid,
            source,
            video_date.isoformat(),
            video_time.isoformat(),
            str(video_path),
            Status.NEW.name,
        ),
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
            source=row[1],
            file_path=row[2],
            status=Status[row[3]],
            classifications=get_classifications(Path(row[2])),
            timestamp=datetime.combine(
                date.fromisoformat(row[4]), time.fromisoformat(row[5])
            ),
        )
        for row in db.execute(
            "SELECT guid, source, video_path, status, date, time FROM videos WHERE status = ?",
            (status.name,),
        )
    ]


def get_videos_by_date_and_source(video_date: date, source: str) -> list[Video]:
    db = _get_db()
    return [
        Video(
            guid=row[0],
            source=row[1],
            file_path=row[2],
            status=Status[row[3]],
            classifications=get_classifications(Path(row[2])),
            timestamp=datetime.combine(
                date.fromisoformat(row[4]), time.fromisoformat(row[5])
            ),
        )
        for row in db.execute(
            """
            SELECT guid, source, video_path, status, date, time
            FROM videos
            WHERE date = ? AND source = ? AND status != 'DELETED'
            """,
            (video_date, source),
        )
    ]


def get_dates() -> list[date]:
    db = _get_db()
    return [
        date.fromisoformat(row[0])
        for row in db.execute(
            "SELECT DISTINCT date FROM videos WHERE status != 'DELETED'"
        )
    ]


def get_sources(video_date: date) -> list[str]:
    db = _get_db()
    return [
        row[0]
        for row in db.execute(
            "SELECT DISTINCT source FROM videos WHERE date = ? AND status != 'DELETED'",
            (video_date,),
        )
    ]


def get_status(video_path: Path) -> Status | None:
    db = _get_db()
    row = db.execute(
        "SELECT status FROM videos WHERE video_path = ?", (str(video_path),)
    ).fetchone()
    return Status[row[0]] if row else None
