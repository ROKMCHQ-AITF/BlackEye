import json
import os
import cv2
from ultralytics import YOLO

Detection = tuple[float, float, float, float, float, str]
Track = tuple[float, float, float, float, int, float, str]

_MODELS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
_TRACKER = os.path.join(_MODELS, "botsort.yaml")


class ShipDetector:
    """
    YOLO 모델로 선박을 탐지하고 트래킹한다.

    담당: AI 팀
    의존: ultralytics, class_labels.json, best.pt, botsort.yaml
    """

    CONFIDENCE_THRESHOLD = 0.25

    def __init__(self, tracker_config: str = _TRACKER):
        self._model = YOLO(os.path.join(_MODELS, "best.pt"))
        self._display_name = self._load_display_names()
        self._tracker_config = tracker_config

    def detect(self, frame: cv2.typing.MatLike) -> list[Detection]:
        results = self._model(frame, verbose=False, conf=self.CONFIDENCE_THRESHOLD)
        return self._parse(results[0].boxes, with_id=False)

    def track(self, frame: cv2.typing.MatLike) -> list[Track]:
        results = self._model.track(frame, tracker=self._tracker_config,
                                    persist=True, verbose=False,
                                    conf=self.CONFIDENCE_THRESHOLD)
        return self._parse(results[0].boxes, with_id=True)  

    def _parse(self, boxes, with_id: bool) -> list:
        out = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            name = self._display_name.get(int(box.cls[0]), "미확인")
            if with_id:
                if box.id is None:
                    continue
                track_id = int(box.id[0])
                out.append((x1, y1, x2, y2, track_id, conf, name))
            else:
                out.append((x1, y1, x2, y2, conf, name))
        return out

    def _load_display_names(self) -> dict[int, str]:
        with open(os.path.join(_MODELS, "class_labels.json"), encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}