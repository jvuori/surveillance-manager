from pathlib import Path

from ultralytics import YOLO


model = YOLO("yolov8s.pt")

def detect_objects(source: Path, save: bool) -> set[str]:
    results = model.track(
        source=source,
        save=save,
        conf=0.5,
        # iou=0.5,
        stream=True,
        verbose=False,
    )

    SKIPPED_CLASSIFICATIONS = ["bench", "chair", "dining table", "traffic light", "bed", "book", "handbag", "donut", "backback", "umbrella"]

    classifications: set[str] = set()
    for result in results:
        for classification in result.boxes.cls.cpu().tolist():
            classification_text = model.names[int(classification)]
            if classification_text not in SKIPPED_CLASSIFICATIONS:
                classifications.add(classification_text)

    return classifications
