import os
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from app.logger import ShipLogger
from app.detector import ShipDetector, Track
from app.config import (
    RENDER_SCALE_BASE, FONT_SIZE_BASE, FONT_SIZE_MIN,
    BOX_WIDTH_BASE, BOX_WIDTH_MIN, LABEL_H_BASE, LABEL_H_MIN,
)

_FONT_PATH = os.path.join(os.environ.get("WINDIR", ""), "Fonts", "malgun.ttf")


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(_FONT_PATH, size=size)
    except OSError:
        return ImageFont.load_default()


class VideoPlaybackThread(QThread):
    """
    영상 파일 또는 RTSP 스트림을 읽고, AI 탐지 결과를 프레임에 그려 Qt 화면으로 내보낸다.

    담당: 비디오 팀
    의존: OpenCV(읽기), Pillow(그리기), ShipDetector(탐지 및 추적), ShipLogger(로그)
    출력: frame_ready, log_ready, video_info_ready 시그널 → window.py
    """

    frame_ready      = pyqtSignal(QPixmap)
    log_ready        = pyqtSignal(str)
    video_info_ready = pyqtSignal(str, int, int, float)  # filename, width, height, fps

    def __init__(self):
        super().__init__()
        self._detector   = ShipDetector()
        self._logger     = ShipLogger()
        self._cap: cv2.VideoCapture | None = None
        self._font       = _load_font(FONT_SIZE_MIN)
        self._ai_enabled = False
        self._running    = False
        self._paused     = False

    # ── 외부 인터페이스 ───────────────────────────────────────────────

    def load(self, source: str) -> bool:
        """파일 경로 또는 RTSP URL을 받아 스트림을 열고 성공 여부를 반환한다."""
        self.stop()
        self.wait()
        self._cap = cv2.VideoCapture(source)
        if not self._cap.isOpened():
            return False

        filename = source if source.startswith("rtsp") else os.path.basename(source)
        w   = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h   = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 30
        self._font = _load_font(max(FONT_SIZE_MIN, int(FONT_SIZE_BASE * max(w, h) / RENDER_SCALE_BASE)))
        self.video_info_ready.emit(filename, w, h, fps)
        return True

    def set_ai(self, enabled: bool) -> None:
        self._ai_enabled = enabled

    def pause(self) -> None:
        self._paused = not self._paused

    def stop(self) -> None:
        self._running = False

    def clear_logger(self) -> None:
        self._logger = ShipLogger()

    # ── 재생 루프 ─────────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        self._paused  = False
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 30
        cached_tracks: list[Track] = []

        while self._running:
            if self._paused:
                time.sleep(0.1)
                continue

            ok, bgr_frame = self._cap.read()
            if not ok:
                break

            if self._ai_enabled:
                cached_tracks = self._detector.track(bgr_frame)
                for x1, y1, x2, y2, track_id, conf, name in cached_tracks:
                    log_msg = self._logger.update(track_id, name)
                    if log_msg:
                        self.log_ready.emit(log_msg)
            else:
                cached_tracks = []

            self.frame_ready.emit(self._render(bgr_frame, cached_tracks))
            time.sleep(1 / fps)

        self._cap.release()
        self._running = False

    # ── 렌더링 (프레임 → QPixmap) ─────────────────────────────────────

    def _render(self, bgr_frame: np.ndarray, tracks: list[Track]) -> QPixmap:
        image = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
        draw  = ImageDraw.Draw(image)

        h, w    = bgr_frame.shape[:2]
        scale   = max(w, h) / RENDER_SCALE_BASE
        box_w   = max(BOX_WIDTH_MIN, int(BOX_WIDTH_BASE * scale))
        label_h = max(LABEL_H_MIN,   int(LABEL_H_BASE   * scale))

        for x1, y1, x2, y2, track_id, conf, name in tracks:
            label = f"[{track_id:03d}] {name} {conf:.2f}"
            draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=box_w)
            draw.rectangle(draw.textbbox((x1, y1 - label_h), label, font=self._font), fill=(0, 255, 0))
            draw.text((x1, y1 - label_h), label, fill=(0, 0, 0), font=self._font)

        rgb = np.array(image)
        h, w, c = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888))
