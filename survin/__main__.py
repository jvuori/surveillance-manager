import argparse
from pathlib import Path

from survin import det

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("--save", action="store_true")
args = parser.parse_args()

detected_objects:set[str] = det.detect_objects(args.source, args.save)
print(detected_objects)
