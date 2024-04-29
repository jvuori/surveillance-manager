import argparse
from pathlib import Path

from survin import det

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path, help="Path to the source directory")
parser.add_argument("--save", action="store_true")
args = parser.parse_args()
if not args.source.is_dir():
    parser.error("source must be a directory")

for file_path in args.source.glob("**/*"):
    if file_path.is_file():
        detected_objects:set[str] = det.detect_objects(file_path, args.save)
        if detected_objects:
            print(file_path, detected_objects)
