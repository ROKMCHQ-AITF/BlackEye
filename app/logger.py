from collections import Counter
from datetime import datetime
from typing import Optional

from app.config import TRACK_ID_WIDTH


class ShipLogger:
    """
    선박 트래킹 결과를 받아서,
    '확정된 함종'이 바뀔 때만 로그 메시지를 만들어주는 클래스.

    ─ 받는 것: track_id(int), detected_name(str)  ← detector.py의 Track 튜플에서 옴
    ─ 주는 것: 로그 문자열(str) 또는 None          ← pipeline.py가 받아서 시그널로 쏴줌
    """

    def __init__(self):
        self._vote_history: dict[int, Counter] = {}
        self._confirmed: dict[int, Optional[str]] = {}

    # ── 외부 인터페이스 ───────────────────────────────────────────────

    def update(self, track_id: int, detected_name: str) -> Optional[str]:
        self._ensure_registered(track_id)
        self._vote_history[track_id][detected_name] += 1

        best_name = self._get_best_name(track_id)
        if best_name != self._confirmed[track_id]:
            self._confirmed[track_id] = best_name
            return self._format_log(track_id, best_name)

        return None

    def reset(self, track_id: int) -> None:
        self._vote_history.pop(track_id, None)
        self._confirmed.pop(track_id, None)

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────

    def _ensure_registered(self, track_id: int) -> None:
        if track_id not in self._vote_history:
            self._vote_history[track_id] = Counter()
            self._confirmed[track_id] = None

    def _get_best_name(self, track_id: int) -> str:
        return self._vote_history[track_id].most_common(1)[0][0]

    def _format_log(self, track_id: int, name: str) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] ID {track_id:0{TRACK_ID_WIDTH}d} | {name} 확인"
