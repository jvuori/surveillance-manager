from datetime import datetime
from enum import StrEnum, auto
from pathlib import Path
from pydantic import BaseModel


class Status(StrEnum):
    NEW = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    DELETED = auto()


class Video(BaseModel):
    guid: str
    source: str
    file_path: Path
    status: Status
    classifications: set[str] = set()
    timestamp: datetime
