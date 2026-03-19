from typing import Protocol


class VideoPlayer(Protocol):
    """
    UI팀과 비디오팀 사이의 계약.

    UI팀은 이 인터페이스만 알면 된다.
    구현이 어떻게 생겼는지는 몰라도 된다.
    """

    frame_ready: object       # 렌더링된 QPixmap을 UI로 전달하는 시그널
    log_ready: object         # 탐지 로그 문자열을 UI로 전달하는 시그널
    video_info_ready: object  # 영상 메타정보(파일명, 해상도, FPS)를 UI로 전달하는 시그널

    def load(self, source: str) -> bool: ...
    # 영상 파일 경로 또는 RTSP URL을 받아 스트림을 열고 성공 여부를 반환한다

    def set_ai(self, enabled: bool) -> None: ...
    # AI 탐지 ON/OFF를 즉시 전환한다. 재생 중에도 호출 가능하다

    def pause(self) -> None: ...
    # 재생을 일시정지하거나 재개한다 (토글)

    def start(self) -> None: ...
    # 재생 스레드를 시작한다

    def stop(self) -> None: ...
    # 재생 스레드를 종료한다

    def wait(self) -> None: ...
    # 재생 스레드가 완전히 종료될 때까지 대기한다

    def clear_logger(self) -> None: ...
    # 트래킹 로그 기록을 초기화한다

    def isRunning(self) -> bool: ...
    # 재생 스레드가 현재 실행 중인지 반환한다
