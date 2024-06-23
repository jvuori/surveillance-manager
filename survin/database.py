from pathlib import Path
import sqlite3
from enum import StrEnum, auto


class Status(StrEnum):
    NEW = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    DELETED = auto()


db = sqlite3.connect("survin.db")
db.execute("CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, status TEXT)")
db.execute("CREATE INDEX IF NOT EXISTS idx_status ON files (status)")
db.execute(
    "CREATE TABLE IF NOT EXISTS classifications (path TEXT, classification TEXT)"
)
db.execute(
    "CREATE INDEX IF NOT EXISTS idx_classification_path ON classifications (path)"
)
db.commit()


def add_file(path: Path):
    db.execute("INSERT INTO files (path) VALUES (?)", (str(path),))
    db.execute(
        "UPDATE files SET status = ? WHERE path = ?", (Status.NEW.name, str(path))
    )
    db.commit()


def set_classifications(path: Path, classifications: set[str]):
    for classification in classifications:
        db.execute(
            "INSERT INTO classifications (path, classification) VALUES (?, ?)",
            (str(path), classification),
        )
    db.commit()


def get_classifications(path: Path) -> set[str]:
    return {
        row[0]
        for row in db.execute(
            "SELECT classification FROM classifications WHERE path = ?", (str(path),)
        )
    }


def set_status(path: Path, status: Status):
    db.execute("UPDATE files SET status = ? WHERE path = ?", (status.name, str(path)))
    db.commit()


def get_files(status: Status) -> list[Path]:
    return [
        Path(row[0])
        for row in db.execute("SELECT path FROM files WHERE status = ?", (status.name,))
    ]


def get_status(path: Path) -> Status | None:
    row = db.execute("SELECT status FROM files WHERE path = ?", (str(path),)).fetchone()
    return Status[row[0]] if row else None
