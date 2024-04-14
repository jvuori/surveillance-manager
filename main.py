import argparse
from pathlib import Path

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("--save", action="store_true")
args = parser.parse_args()

model = YOLO("yolov8s.pt")

results = model.track(
    source=args.source,
    save=args.save,
    conf=0.5,
    # iou=0.5,
    stream=True,
    verbose=False,
)

SKIPPED_CLASSIFICATIONS = ["bench", "chair"]

classifications = set()
for result in results:
    for classification in result.boxes.cls.cpu().tolist():
        classification_text = model.names[int(classification)]
        if classification_text not in SKIPPED_CLASSIFICATIONS:
            classifications.add(classification_text)

print(classifications)
