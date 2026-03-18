from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFileDialog, QSlider,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from app.interfaces import VideoPlayer


class MainWindow(QMainWindow):
    """
    애플리케이션 최상위 창.

    담당: UI 팀
    의존: VideoPlayer 인터페이스 (구현체가 무엇인지 몰라도 된다)
    규칙: 이 파일은 UI 레이아웃과 사용자 이벤트 처리만 담당한다.
          비즈니스 로직은 pipeline.py 또는 detector.py에 둔다.

    ──────────────────────────────────────────────────────────────────────

                        ┌─────────────────────────────────┐
                        │                                 │ <- header
                        ├──────────────────────┬──────────┤
                        │                      │          │
    _video_screen ->    │                      │          │
                        │                      │          │ <- right_layout
                        │                      │          │
                        ├──────────────────────┤          │
    controls_layout ->  │                      │          │
                        └──────────────────────┴──────────┘

    260318
     - 헤더 추가
     - QSlider 추가 임포트
     - 영상 재생바, 영상 컨트롤러 추가 
        ㄴ 김승휘는 기능 구현할 것

    """

    def __init__(self, player: VideoPlayer):
        super().__init__()
        self.setWindowTitle("BlackEye")
        self.resize(1100, 700)

        self._pipeline = player
        self._pipeline.frame_ready.connect(self._on_frame_ready)
        self._pipeline.finished.connect(self._on_playback_finished)

        self.setCentralWidget(self._build_ui())

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _build_ui(self) -> QWidget:
        self._video_screen = VideoScreen()
        self._video_slider = self._make_video_slider()
        self._time_label = self._make_time_label()
        self._btn_video_back = self._make_video_back_button()
        self._btn_video_play = self._make_video_play_button()
        self._btn_video_forward = self._make_video_forward_button()
        self._btn_load = self._make_load_button()
        self._btn_ai = self._make_ai_toggle_button()

        # 좌측 하단 컨트롤 레이아웃
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self._video_slider)
        controls_layout.addWidget(self._time_label)
        controls_layout.addWidget(self._btn_video_back)
        controls_layout.addWidget(self._btn_video_play)
        controls_layout.addWidget(self._btn_video_forward)

        # 좌측 레이아웃
        left_layout = QVBoxLayout()
        left_layout.addWidget(self._video_screen)   
        left_layout.addLayout(controls_layout)

        # 우측 레이아웃
        right_layout = QVBoxLayout()
        right_layout.addWidget(self._btn_load)
        right_layout.addStretch()
        right_layout.addWidget(self._btn_ai)
        
        # 바디 레이아웃
        body = QHBoxLayout()
        body.addLayout(left_layout, stretch=4)
        body.addLayout(right_layout, stretch=1)

        # 헤더 레이아웃
        header = QLabel("서북도서객체탐지체계")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFixedHeight(30)
        header.setStyleSheet("color:white; font-size:20px; font-weight:bold;")

        # 전체 레이아웃
        root = QVBoxLayout()
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)
        root.addWidget(header)
        root.addLayout(body)

        container = QWidget()
        container.setStyleSheet("background-color:#1e1e1e;")
        container.setLayout(root)
        return container

    # ── 버튼 구현 ───────────────────────────────────────────────────────
    def _make_video_slider(self) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setFixedHeight(45)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #444;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #cc0000;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -4px 0;
                background: white;
                border-radius: 7px;
            }
        """)
        return slider
    
    def _make_time_label(self) -> QLabel:
        label = QLabel("00:00 / 00:00")
        label.setFixedWidth(70)
        label.setStyleSheet("color:white; font-size:11px;")
        return label

    def _make_video_back_button(self) -> QPushButton:
        btn = QPushButton("<<")
        btn.setFixedHeight(45)
        btn.setFixedWidth(45)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        return btn

    def _make_video_play_button(self) -> QPushButton:
        btn = QPushButton("▶")
        btn.setFixedHeight(45)
        btn.setFixedWidth(45)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        btn.clicked.connect(self._on_video_play_clicked)
        return btn

    def _make_video_forward_button(self) -> QPushButton:
        btn = QPushButton(">>")
        btn.setFixedHeight(45)
        btn.setFixedWidth(45)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        return btn
    
    def _make_load_button(self) -> QPushButton:
        btn = QPushButton("영상 불러오기")
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; }
            QPushButton:hover { background:#444; }
        """)
        btn.clicked.connect(self._on_load_clicked)
        return btn

    def _make_ai_toggle_button(self) -> QPushButton:
        btn = QPushButton("AI 탐지")
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton         { color:white; font-weight:bold; border-radius:5px; }
            QPushButton:hover { background:#444; }
            QPushButton:checked { background:#cc0000; }
        """)
        btn.toggled.connect(self._on_ai_toggled)
        return btn

    # ── 이벤트 핸들러 ─────────────────────────────────────────────────
    def _on_video_play_clicked(self) -> None:
        if self._btn_video_play.text() == "▶":
            self._btn_video_play.setText("■")
        else:
            self._btn_video_play.setText("▶")

    def _on_load_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "비디오 파일 선택")
        if file_path and self._pipeline.load(file_path):    
            self._pipeline.start()

    def _on_ai_toggled(self, enabled: bool) -> None:
        self._pipeline.set_ai(enabled)

    def _on_frame_ready(self, pixmap: QPixmap) -> None:
        self._video_screen.show_frame(pixmap)

    def _on_playback_finished(self) -> None:
        self._btn_ai.setChecked(False)

    # ── 창 종료 처리 ──────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._pipeline.stop()
        self._pipeline.wait()
        super().closeEvent(event)


class VideoScreen(QLabel):
    """
    QPixmap을 받아 화면에 표시하는 단순 위젯.
    크기 변화에 맞춰 비율을 유지하며 스케일링한다.
    """

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setText("영상이 여기에 표시됩니다.")
        self.setStyleSheet("""
            background:black; color:white;
            border:2px solid #444; font-size:16px; font-weight:bold;
        """)

    def show_frame(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
