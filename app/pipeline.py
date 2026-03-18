import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from app.logger import ShipLogger
from app.detector import ShipDetector, Track


class VideoPlaybackThread(QThread):
    """
    영상 파일을 읽고, AI 탐지 결과를 프레임에 그려 Qt 화면으로 내보내고, 실시간 로그를 내보냄.

    담당: 비디오 팀
    의존: OpenCV(읽기), Pillow(그리기), ShipDetector(탐지 및 추적), ShipLogger(실시간 로그 계산)
    출력: frame_ready 시그널 → window.py의 VideoScreen
    """

    frame_ready = pyqtSignal(QPixmap)
    log_ready = pyqtSignal(str) 
    DETECTION_INTERVAL = 5

    def __init__(self):
        super().__init__()
        self._detector = ShipDetector()
        self._cap: cv2.VideoCapture | None = None
        self._logger = ShipLogger()
        self._ai_enabled = False
        self._running = False

    # ── 외부 인터페이스 ───────────────────────────────────────────────

    def load(self, file_path: str) -> bool:
        self.stop()
        self.wait()
        self._cap = cv2.VideoCapture(file_path)
        return self._cap.isOpened()

    def set_ai(self, enabled: bool) -> None:
        self._ai_enabled = enabled

    def stop(self) -> None:
        self._running = False

    # ── 재생 루프 ─────────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 30
        cached_tracks: list[Track] = []
        frame_index = 0

        while self._running:
            ok, bgr_frame = self._cap.read()
            if not ok:
                break

            if self._ai_enabled:
                cached_tracks = self._detector.track(bgr_frame)
                
                for track in cached_tracks:
                    x1, y1, x2, y2, track_id, conf, name = track
                    log_msg = self._logger.update(track_id, name)
                    if log_msg:
                        self.log_ready.emit(log_msg)
            elif not self._ai_enabled:
                cached_tracks = []

            self.frame_ready.emit(self._render(bgr_frame, cached_tracks))
            time.sleep(1 / fps)
            frame_index += 1

        self._cap.release()
        self._running = False

    # ── 렌더링 ────────────────────────────────────────────────────────

    def _render(self, bgr_frame: np.ndarray, tracks: list[Track]) -> QPixmap:
        image = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)

        h, w = bgr_frame.shape[:2]
        scale = max(w, h) / 1000          # 해상도 기준 비율
        font_size = max(20, int(24 * scale))
        box_width = max(2, int(3 * scale))
        label_h = max(30, int(35 * scale))

        font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size=font_size)

        for x1, y1, x2, y2, track_id, conf, name in tracks:
            label = f"[{track_id}] {name} {conf:.2f}"
            draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=box_width)
            draw.rectangle(draw.textbbox((x1, y1 - label_h), label, font=font), fill=(0, 255, 0))
            draw.text((x1, y1 - label_h), label, fill=(0, 0, 0), font=font)

        rgb = np.array(image)
        h, w, c = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888))
