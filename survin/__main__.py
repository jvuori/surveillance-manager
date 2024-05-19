import argparse
from pathlib import Path

from survin import det


def _handle_file(file_path: Path, save: bool) -> None:
    detected_objects: set[str] = det.detect_objects(file_path, save)
    if detected_objects:
        print(file_path, detected_objects)


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
