from typing import Protocol
from PyQt6.QtGui import QPixmap


class VideoPlayer(Protocol):
    """
    UI팀과 비디오팀 사이의 계약.

    UI팀은 이 인터페이스만 알면 된다.
    구현이 어떻게 생겼는지는 몰라도 된다.
    """

    frame_ready: object  # pyqtSignal(QPixmap)

    def load(self, file_path: str) -> bool: ...
    def set_ai(self, enabled: bool) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def wait(self) -> None: ...
    def clear_logger(self) -> None: ...
