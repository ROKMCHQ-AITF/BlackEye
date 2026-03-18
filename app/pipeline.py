import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from app.detector import ShipDetector, Detection


class VideoPlaybackThread(QThread):
    """
    영상 파일을 읽고, AI 탐지 결과를 프레임에 그려 Qt 화면으로 내보낸다.

    담당: 비디오 팀
    의존: OpenCV(읽기), Pillow(그리기), ShipDetector(탐지)
    출력: frame_ready 시그널 → window.py의 VideoScreen
    """

    frame_ready = pyqtSignal(QPixmap)

    # YOLO 추론을 매 N프레임마다 한 번 실행한다.
    # 중간 프레임은 직전 탐지 결과를 재사용한다.
    # 성능에 따라 조정 필요: 낮을수록 정확하지만 느림
    DETECTION_INTERVAL = 5

    def __init__(self):
        super().__init__()
        self._detector = ShipDetector()
        self._cap: cv2.VideoCapture | None = None
        self._ai_enabled = False
        self._running = False

    # ── 외부 인터페이스 ───────────────────────────────────────────────

    def load(self, file_path: str) -> bool:
        """영상 파일을 열고 성공 여부를 반환한다."""
        self.stop()
        self.wait()
        self._cap = cv2.VideoCapture(file_path)
        return self._cap.isOpened()

    def set_ai(self, enabled: bool) -> None:
        """재생 중에도 즉시 AI 탐지 ON/OFF를 전환한다."""
        self._ai_enabled = enabled

    def stop(self) -> None:
        self._running = False

    # ── 재생 루프 ─────────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 30
        cached_detections: list[Detection] = []
        frame_index = 0

        while self._running:
            ok, bgr_frame = self._cap.read()
            if not ok:
                break

            if self._ai_enabled and frame_index % self.DETECTION_INTERVAL == 0:
                cached_detections = self._detector.detect(bgr_frame)
            elif not self._ai_enabled:
                cached_detections = []

            self.frame_ready.emit(self._render(bgr_frame, cached_detections))
            time.sleep(1 / fps)
            frame_index += 1

        self._cap.release()
        self._running = False

    # ── 렌더링 (프레임 → QPixmap) ─────────────────────────────────────

    def _render(self, bgr_frame: np.ndarray, detections: list[Detection]) -> QPixmap:
        image = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)

        for x1, y1, x2, y2, conf, name in detections:
            label = f"{name} {conf:.2f}"
            draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
            draw.rectangle(draw.textbbox((x1, y1 - 25), label), fill=(0, 255, 0))
            draw.text((x1, y1 - 25), label, fill=(0, 0, 0))

        rgb = np.array(image)
        h, w, c = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888))
