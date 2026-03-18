# logger.py

from collections import Counter
from datetime import datetime
from typing import Optional


class ShipLogger:
    """
    선박 트래킹 결과를 받아서,
    '확정된 함종'이 바뀔 때만 로그 메시지를 만들어주는 클래스.

    ─ 받는 것: track_id(int), detected_name(str)  ← detector.py의 Track 튜플에서 옴
    ─ 주는 것: 로그 문자열(str) 또는 None          ← pipeline.py가 받아서 시그널로 쏴줌
    """

    def __init__(self):
        # { track_id: Counter({ "어선": 5, "경비함": 2 }) }
        # 역할: 매 프레임마다 찍힌 함종 기록 누적
        self._vote_history: dict[int, Counter] = {}

        # { track_id: "어선" }
        # 역할: 마지막으로 '확정'된 함종 기억 → 변경 감지에만 씀
        self._confirmed: dict[int, Optional[str]] = {}

    # ── 외부 인터페이스 (pipeline.py가 호출) ─────────────────────────

    def update(self, track_id: int, detected_name: str) -> Optional[str]:
        """
        프레임마다 호출됨. 확정 함종이 바뀌었으면 로그 문자열 반환, 아니면 None.

        왜 Optional[str]?
        → 매 프레임마다 로그를 찍으면 UI가 도배됨.
          '처음 등장' or '함종이 바뀜' 이 두 경우에만 의미있는 이벤트임.
        """
        self._ensure_registered(track_id)
        self._vote_history[track_id][detected_name] += 1

        best_name = self._get_best_name(track_id)

        if best_name != self._confirmed[track_id]:
            self._confirmed[track_id] = best_name
            return self._format_log(track_id, best_name)  # 변경 있을 때만 반환

        return None  # 변경 없으면 조용히 None

    def reset(self, track_id: int) -> None:
        """
        특정 ID가 화면에서 사라졌을 때 기록 초기화.
        (선택적으로 pipeline.py에서 호출)
        """
        self._vote_history.pop(track_id, None)
        self._confirmed.pop(track_id, None)

    # ── 내부 헬퍼 (이 클래스 안에서만 씀) ───────────────────────────

    def _ensure_registered(self, track_id: int) -> None:
        """
        처음 보는 track_id면 장부 초기화.

        왜 별도 메서드?
        → update()가 '데이터 갱신 + 변경 감지 + 포맷팅' 까지 하면 너무 길어짐.
          초기화 책임만 여기서 담당. (SRP: 단일 책임 원칙)
        """
        if track_id not in self._vote_history:
            self._vote_history[track_id] = Counter()
            self._confirmed[track_id] = None

    def _get_best_name(self, track_id: int) -> str:
        """
        지금까지 가장 많이 찍힌 함종 반환.

        Counter.most_common(1) → [("어선", 5)]  리스트
        [0]                    → ("어선", 5)    첫 번째 튜플
        [0]                    → "어선"         이름만
        """
        return self._vote_history[track_id].most_common(1)[0][0]

    def _format_log(self, track_id: int, name: str) -> str:
        """
        UI에 표시할 문자열 포맷. 시간, ID, 함종 포함.

        왜 별도 메서드?
        → 나중에 포맷 바꿔도 여기만 수정하면 됨. (OCP: 개방-폐쇄 원칙)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] ID {track_id:03d} | {name} 확인"