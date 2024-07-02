import argparse
from pathlib import Path
from datetime import date, datetime, time, timedelta
import re

from survin import det, database


def _save_snapshot_picture_from_video(video_path: Path, save_path: Path):
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    desired_frame = total_frames // 4  # 25% of the video
    cap.set(cv2.CAP_PROP_POS_FRAMES, desired_frame)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(str(save_path), frame)
    cap.release()


def _handle_deleted_files() -> None:
    for file_path in database.get_video_paths_by_status(
        status=database.Status.COMPLETED
    ) + database.get_video_paths_by_status(status=database.Status.NEW):
        if not file_path.exists():
            print("Mark file as deleted:", file_path)
            database.set_status(file_path, database.Status.DELETED)
            snapshot_file_path = Path("snapshots").joinpath(
                file_path.with_suffix(".jpg").name
            )
            print("Deleting snapshot:", snapshot_file_path)
            snapshot_file_path.unlink(missing_ok=True)


def _get_date_time_from_file_name(file_path: Path) -> tuple[date, time]:
    date_match = re.search(r"___(\d{4}-\d{2}-\d{2})___", file_path.name)
    time_match = re.search(r"___(\d{2}-\d{2}-\d{2})", file_path.name)
    if not date_match or not time_match:
        raise ValueError("Date or time not determined from file name")
    video_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
    video_time = datetime.strptime(time_match.group(1), "%H-%M-%S")
    return video_date.date(), video_time.time()


def _get_source_from_file_name(file_path: Path) -> str:
    source_match = re.search(r"(.+?)___", file_path.name)
    if not source_match:
        raise ValueError("Source not determined from file name")
    return source_match.group(1)


def _check_file_status(file_path: Path) -> None:
    file_size = file_path.stat().st_size
    if file_size < 1024 * 1024:
        print("Delete too small file:", file_path)
        file_path.unlink()
        return

    if not file_path.exists():
        database.set_status(file_path, database.Status.DELETED)
        print("File no longer exists. Mark as deleted:", file_path)
        return

    status = database.get_status(file_path)
    if database.get_status(file_path) is None:
        print("New file found:", file_path)
        source = _get_source_from_file_name(file_path)
        print("  Source:", source)
        video_date, video_time = _get_date_time_from_file_name(file_path)
        print("  Date:", video_date)
        print("  Time:", video_time)
        database.add_video(
            video_path=file_path,
            source=source,
            video_date=video_date,
            video_time=video_time,
        )
        status = database.Status.NEW

    snapshot_file_path = Path("snapshots").joinpath(file_path.with_suffix(".jpg").name)
    snapshot_file_path.parent.mkdir(parents=True, exist_ok=True)

    if status == database.Status.COMPLETED:
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        if database.get_classifications(file_path):
            max_age = timedelta(days=5)
        else:
            max_age = timedelta(days=2)
        if datetime.now(tz=modified_time.tzinfo) - modified_time > max_age:
            print("Mark file as deleted:", file_path)
            database.set_status(file_path, database.Status.DELETED)
            status = database.Status.DELETED

    if status == database.Status.DELETED:
        print("Deleting file:", file_path)
        file_path.unlink()
        print("Deleting snapshot:", snapshot_file_path)
        snapshot_file_path.unlink(missing_ok=True)
    elif not snapshot_file_path.exists():
        print("Creating snapshot:", snapshot_file_path)
        _save_snapshot_picture_from_video(file_path, snapshot_file_path)


def _process_file(file_path: Path, save: bool, reprocess: bool) -> None:
    status = database.get_status(file_path)

    if status == database.Status.NEW or reprocess:
        print("Processing file:", file_path)
        detected_objects: set[str] = det.detect_objects(file_path, save)
        print("Detected objects:", detected_objects)
        database.set_classifications(file_path, detected_objects)
        database.set_status(file_path, database.Status.COMPLETED)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the source file or directory",
    )
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--reprocess", "-r", action="store_true")
    args = parser.parse_args()

    database.create_db()

    _handle_deleted_files()

    if args.source.is_dir():
        for file_path in args.source.glob("**/*.mkv"):
            _check_file_status(file_path)
        for file_path in args.source.glob("**/*.mkv"):
            _process_file(file_path, args.save, args.reprocess)
    else:
        file_path = args.source
        _check_file_status(file_path)
        _process_file(file_path, args.save, args.reprocess)


if __name__ == "__main__":
    main()
