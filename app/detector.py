import json
import os
import cv2
from ultralytics import YOLO

# 탐지 결과 한 건을 나타내는 타입 별칭
# (x1, y1, x2, y2, confidence, display_name)
Detection = tuple[float, float, float, float, float, str]

_MODELS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")


class ShipDetector:
    """
    YOLO 모델로 프레임에서 선박을 탐지한다.

    담당: AI 팀
    의존: ultralytics, class_labels.json, best.pt
    """

    CONFIDENCE_THRESHOLD = 0.25

    def __init__(self):
        self._model = YOLO(os.path.join(_MODELS, "best.pt"))
        self._display_name = self._load_display_names()

    def detect(self, frame: cv2.typing.MatLike) -> list[Detection]:
        """BGR 프레임을 받아 탐지 결과 목록을 반환한다."""
        results = self._model(frame, verbose=False, conf=self.CONFIDENCE_THRESHOLD)
        detections = []

        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            name = self._display_name.get(int(box.cls[0]), "미확인")
            detections.append((x1, y1, x2, y2, conf, name))

        return detections

    def _load_display_names(self) -> dict[int, str]:
        """class_labels.json에서 {class_id: 한글명} 딕셔너리를 만든다."""
        with open(os.path.join(_MODELS, "class_labels.json"), encoding="utf-8") as f:
            data = json.load(f)

        return {int(class_id): name for class_id, name in data.items()}
