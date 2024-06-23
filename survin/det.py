from functools import cache
from pathlib import Path


@cache
def _get_model():
    from ultralytics import YOLO

    return YOLO("yolov8s.pt")


SKIPPED_CLASSIFICATIONS = [
    "airplane",
    "backpack",
    "banana",
    "baseball glove",
    "bed",
    "bench",
    "book",
    "bottle",
    "bowl",
    "cake",
    "cell phone",
    "chair",
    "couch",
    "dining table",
    "donut",
    "frisbee",
    "handbag",
    "hot dog",
    "parking meter",
    "potted plant",
    "refrigerator",
    "skateboard",
    "sports ball",
    "stop sign",
    "suitcase",
    "tennis racket",
    "toilet",
    "traffic light",
    "train",
    "umbrella",
    "vase",
]


def detect_objects(source: Path, save: bool) -> set[str]:
    model = _get_model()
    results = model.track(
        source=source,
        save=save,
        conf=0.5,
        # iou=0.5,
        stream=True,
        verbose=False,
    )

    classifications: set[str] = set()
    for result in results:
        for classification in result.boxes.cls.cpu().tolist():
            classification_text = model.names[int(classification)]
            if classification_text not in SKIPPED_CLASSIFICATIONS:
                classifications.add(classification_text)

    return classifications
