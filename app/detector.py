import json
import os
import cv2
from ultralytics import YOLO

from app.config import CONFIDENCE_THRESHOLD

Track     = tuple[float, float, float, float, int, float, str]

_MODELS  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
_TRACKER = os.path.join(_MODELS, "botsort.yaml")


class ShipDetector:
    """
    YOLO 모델로 선박을 탐지하고 트래킹한다.

    담당: AI 팀
    의존: ultralytics, class_labels.json, best.pt, botsort.yaml
    """

    def __init__(self, tracker_config: str = _TRACKER):
        model_path  = os.path.join(_MODELS, "best.pt")
        labels_path = os.path.join(_MODELS, "class_labels.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"모델 파일 없음: {model_path}")
        if not os.path.exists(labels_path):
            raise FileNotFoundError(f"레이블 파일 없음: {labels_path}")
        if not os.path.exists(tracker_config):
            raise FileNotFoundError(f"트래커 설정 없음: {tracker_config}")

        self._model          = YOLO(model_path)
        self._display_name   = self._load_display_names(labels_path)
        self._tracker_config = tracker_config

    def track(self, frame: cv2.typing.MatLike) -> list[Track]:
        """BGR 프레임을 받아 트래킹 결과 목록을 반환한다."""
        results = self._model.track(frame, tracker=self._tracker_config,
                                    persist=True, verbose=False,
                                    conf=CONFIDENCE_THRESHOLD)
        out = []
        for box in results[0].boxes:
            if box.id is None:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            out.append((x1, y1, x2, y2, int(box.id[0]), float(box.conf[0]),
                        self._display_name.get(int(box.cls[0]), "미확인")))
        return out

    @staticmethod
    def _load_display_names(labels_path: str) -> dict[int, str]:
        with open(labels_path, encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
