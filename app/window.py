from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFileDialog, QSlider, QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

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

    video_name.mp4 
    1920x1080 @ 30 Hz

    """

    def __init__(self, player: VideoPlayer):
        super().__init__()
        self.setWindowIcon(QIcon("Blackeye.ico"))
        self.setWindowTitle("BlackEye")
        self.resize(1100, 700)

        self._pipeline = player
        self._pipeline.frame_ready.connect(self._on_frame_ready)
        self._pipeline.log_ready.connect(self._on_log_ready)
        self._pipeline.finished.connect(self._on_playback_finished)

        self.setCentralWidget(self._build_ui())

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _build_ui(self) -> QWidget:
        self._title = self._make_title()
        self._logo = self._make_logo()
        self._video_screen = VideoScreen()
        self._video_slider = self._make_video_slider()
        self._time_label = self._make_time_label()
        self._btn_video_back = self._make_video_back_button()
        self._btn_video_play = self._make_video_play_button()
        self._btn_video_forward = self._make_video_forward_button()
        self._btn_ai = self._make_ai_toggle_button()
        self._btn_log_reset = self._make_btn_log_reset()
        self._ai_log = self._make_ai_log()
        self._btn_load_rtsp = self._make_load_rtsp_button()
        self._btn_load = self._make_load_button()

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
        right_layout.addWidget(self._btn_ai)
        right_layout.addWidget(self._btn_log_reset)
        right_layout.addWidget(self._ai_log, stretch=1)
        right_layout.addWidget(self._btn_load_rtsp)
        right_layout.addWidget(self._btn_load)
        
        # 바디 레이아웃
        body = QHBoxLayout()
        body.addLayout(left_layout, stretch=4)
        body.addLayout(right_layout, stretch=1)

        # 헤더 레이아웃
        header = QHBoxLayout()
        header.addWidget(self._logo)
        header.addWidget(self._title)

        # 전체 레이아웃
        root = QVBoxLayout()
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)
        root.addLayout(header)
        root.addLayout(body)

        container = QWidget()
        container.setStyleSheet("background-color:#1e1e1e;")
        container.setLayout(root)
        return container

    # ── 버튼 구현 ───────────────────────────────────────────────────────
    def _make_logo(self) -> QLabel:
        logo = QLabel()
        pixmap = QPixmap("rokmc.png").scaled(
            35, 35,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(pixmap)
        logo.setFixedSize(35, 35)
        return logo

    def _make_title(self) -> QLabel:
        title = QLabel("서북도서객체탐지체계")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("color:white; font-size:20px; font-weight:bold;")
        return title

    def _make_video_slider(self) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setFixedHeight(40)
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
        btn.setFixedHeight(40)
        btn.setFixedWidth(40)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        return btn

    def _make_video_play_button(self) -> QPushButton:
        btn = QPushButton("▶")
        btn.setFixedHeight(40)
        btn.setFixedWidth(40)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        btn.clicked.connect(self._on_video_play_clicked)
        return btn

    def _make_video_forward_button(self) -> QPushButton:
        btn = QPushButton(">>")
        btn.setFixedHeight(40)
        btn.setFixedWidth(40)
        btn.setStyleSheet("""
                QPushButton { color:white; font-weight:bold; border-radius:5px; }
                QPushButton:hover { background:#444; }
            """)
        return btn
    
    def _make_ai_toggle_button(self) -> QPushButton:
        btn = QPushButton("AI 탐지 OFF")
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton         { color:white; font-weight:bold; border-radius:5px; font-size:15px; border: 1px solid #444; }
            QPushButton:hover { background:#444; }
            QPushButton:checked { background:#cc0000; }
        """)
        btn.toggled.connect(self._on_ai_toggled)
        return btn
    
    def _make_btn_log_reset(self) -> QPushButton:
        btn = QPushButton("로그 지우기")
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; font-size:15px; border: 1px solid #444; }
            QPushButton:hover { background:#444; }
        """)
        btn.clicked.connect(self._on_ai_log_clear)
        return btn

    def _make_ai_log(self) -> QTextEdit:
        log = QTextEdit()
        log.setReadOnly(True)
        log.setAlignment(Qt.AlignmentFlag.AlignBottom)
        log.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        return log
    
    def _make_load_rtsp_button(self) -> QPushButton:
        btn = QPushButton("RTSP 불러오기")
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; font-size:15px; border: 1px solid #444; }
            QPushButton:hover { background:#444; }
        """)
        return btn
    
    def _make_load_button(self) -> QPushButton:
        btn = QPushButton("영상 불러오기")
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; font-size:15px; border: 1px solid #444; }
            QPushButton:hover { background:#444; }
        """)
        btn.clicked.connect(self._on_load_clicked)
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
            filename = file_path.split("/")[-1]
            self._video_screen.set_video_info(filename, 1920, 1080, 30.0)

    def _on_ai_toggled(self, enabled: bool) -> None:
        self._btn_ai.setText(f"AI 탐지: {'ON' if enabled else 'OFF'}")
        self._pipeline.set_ai(enabled)

    def _on_frame_ready(self, pixmap: QPixmap) -> None:
        self._video_screen.show_frame(pixmap)

    def _on_playback_finished(self) -> None:
        self._btn_ai.setChecked(False)

    def _on_ai_log_clear(self) -> None:
        self._ai_log.clear()
        self._pipeline.clear_logger()
    
    def _on_log_ready(self, msg: str) -> None:
        self._ai_log.append(msg)

    # ── 창 종료 처리 ──────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._pipeline.stop()
        self._pipeline.wait()
        super().closeEvent(event)

# ── 플레이 ──────────────────────────────────────────────────

class VideoScreen(QLabel):
    """
    QPixmap을 받아 화면에 표시하는 단순 위젯.
    크기 변화에 맞춰 비율을 유지하며 스케일링한다.
    """

    def __init__(self):
        super().__init__()
        self._setup_screen()
        self._overlay = self._make_overlay()

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _setup_screen(self) -> None:
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setText("영상이 여기에 표시됩니다.")
        self.setStyleSheet("""
            background:black; color:white;
            font-size:16px; font-weight:bold;
        """)

    def _make_overlay(self) -> QLabel:
        overlay = QLabel(self)
        overlay.setStyleSheet("""
            color: white;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 128);
        """)
        overlay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        overlay.adjustSize()
        overlay.hide()
        return overlay

    # ── 이벤트 ────────────────────────────────────────────────────

    def show_frame(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def set_video_info(self, filename: str, width: int, height: int, fps: float) -> None:
        self._overlay.setText(
            f"{filename}\n{width}x{height} @ {fps:.1f}Hz"
        )
        self._overlay.adjustSize()
        self._overlay.show()

    def clear_video_info(self) -> None:
        self._overlay.hide()