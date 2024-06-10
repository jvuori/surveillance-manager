import argparse
from pathlib import Path

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


def _handle_file(file_path: Path, save: bool) -> None:
    file_size = file_path.stat().st_size
    if file_size < 1024 * 1024:
        print("Deleting file:", file_path, "because it's too small")
        file_path.unlink()
        return

    if database.get_status(file_path) is None:
        database.add_file(file_path)

    if database.get_status(file_path) == database.Status.NEW:
        print("Processing file:", file_path)
        detected_objects: set[str] = det.detect_objects(file_path, save)
        print("Detected objects:", detected_objects)
        database.set_classifications(file_path, detected_objects)
        database.set_status(file_path, database.Status.COMPLETED)

    snapshot_file_path = Path("snapshots").joinpath(file_path.with_suffix(".jpg").name)
    snapshot_file_path.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot_file_path.exists():
        print("Creating snapshot:", snapshot_file_path)
        _save_snapshot_picture_from_video(file_path, snapshot_file_path)

    if database.get_status(file_path) == database.Status.DELETED:
        print("Deleting file:", file_path)
        file_path.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the source file or directory",
    )
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    if args.source.is_dir():
        for file_path in args.source.glob("**/*"):
            if file_path.is_file():
                _handle_file(file_path, args.save)
    else:
        _handle_file(args.source, args.save)


if __name__ == "__main__":
    main()
