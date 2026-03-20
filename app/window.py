from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFileDialog, QSlider, QTextEdit,
    QDialog, QDialogButtonBox, QLineEdit,
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
    """

    def __init__(self, player: VideoPlayer):
        super().__init__()
        self.setWindowIcon(QIcon("blackeye.ico"))
        self.setWindowTitle("BlackEye")
        self.resize(1100, 700)

        self._pipeline = player
        self._pipeline.frame_ready.connect(self._on_frame_ready)
        self._pipeline.log_ready.connect(self._on_log_ready)
        self._pipeline.video_info_ready.connect(self._on_video_info_ready)
        self._pipeline.finished.connect(self._on_playback_finished)

        self.setCentralWidget(self._build_ui())

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _build_ui(self) -> QWidget:
        self._logo              = self._make_logo()
        self._title             = self._make_title()
        self._video_screen      = VideoScreen()
        self._video_slider      = self._make_video_slider()
        self._time_label        = self._make_time_label()
        self._btn_video_back    = self._make_video_back_button()
        self._btn_video_play    = self._make_video_play_button()
        self._btn_video_forward = self._make_video_forward_button()
        self._btn_ai            = self._make_ai_toggle_button()
        self._btn_log_reset     = self._make_btn_log_reset()
        self._ai_log            = self._make_ai_log()
        self._btn_source        = self._make_source_button()

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self._video_slider)
        controls_layout.addWidget(self._time_label)
        controls_layout.addWidget(self._btn_video_back)
        controls_layout.addWidget(self._btn_video_play)
        controls_layout.addWidget(self._btn_video_forward)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._video_screen)
        left_layout.addLayout(controls_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self._btn_ai)
        right_layout.addWidget(self._btn_log_reset)
        right_layout.addWidget(self._ai_log, stretch=1)
        right_layout.addWidget(self._btn_source)

        body = QHBoxLayout()
        body.addLayout(left_layout, stretch=4)
        body.addLayout(right_layout, stretch=1)

        header = QHBoxLayout()
        header.addWidget(self._logo)
        header.addWidget(self._title)

        root = QVBoxLayout()
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)
        root.addLayout(header)
        root.addLayout(body)

        container = QWidget()
        container.setStyleSheet("background-color:#1e1e1e;")
        container.setLayout(root)
        return container

    # ── 위젯 생성 ─────────────────────────────────────────────────────

    def _make_logo(self) -> QLabel:
        logo = QLabel()
        pixmap = QPixmap("rokmc.png").scaled(
            35, 35,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
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
            QSlider::groove:horizontal { height:6px; background:#444; border-radius:3px; }
            QSlider::sub-page:horizontal { background:#cc0000; border-radius:3px; }
            QSlider::handle:horizontal { width:14px; height:14px; margin:-4px 0; background:white; border-radius:7px; }
        """)
        return slider

    def _make_time_label(self) -> QLabel:
        label = QLabel("00:00 / 00:00")
        label.setFixedWidth(70)
        label.setStyleSheet("color:white; font-size:11px;")
        return label

    def _make_control_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; }
            QPushButton:hover { background:#444; }
        """)
        return btn

    def _make_video_back_button(self) -> QPushButton:
        return self._make_control_button("<<")

    def _make_video_play_button(self) -> QPushButton:
        btn = self._make_control_button("▶")
        btn.clicked.connect(self._on_video_play_clicked)
        return btn

    def _make_video_forward_button(self) -> QPushButton:
        return self._make_control_button(">>")

    def _make_side_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; font-size:15px; border:1px solid #444; }
            QPushButton:hover { background:#444; }
        """)
        return btn

    def _make_ai_toggle_button(self) -> QPushButton:
        btn = QPushButton("AI 탐지 OFF")
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton         { color:white; font-weight:bold; border-radius:5px; font-size:15px; border:1px solid #444; }
            QPushButton:hover   { background:#444; }
            QPushButton:checked { background:#cc0000; }
        """)
        btn.toggled.connect(self._on_ai_toggled)
        return btn

    def _make_btn_log_reset(self) -> QPushButton:
        btn = self._make_side_button("로그 지우기")
        btn.clicked.connect(self._on_ai_log_clear)
        return btn

    def _make_ai_log(self) -> QTextEdit:
        log = QTextEdit()
        log.setReadOnly(True)
        log.setStyleSheet("""
            QTextEdit {
                background-color:#2a2a2a; color:white;
                border:1px solid #444; border-radius:5px; font-size:12px;
            }
        """)
        return log

    def _make_source_button(self) -> QPushButton:
        btn = self._make_side_button("소스 불러오기")
        btn.clicked.connect(self._on_source_clicked)
        return btn

    # ── 이벤트 핸들러 ─────────────────────────────────────────────────

    def _on_video_play_clicked(self) -> None:
        is_playing = self._btn_video_play.text() == "▶"
        self._btn_video_play.setText("■" if is_playing else "▶")
        self._pipeline.pause()

    def _on_source_clicked(self) -> None:
        dialog = SourceDialog(self)
        if dialog.exec() and dialog.get_source():
            source = dialog.get_source()
            if self._pipeline.load(source):
                is_file = not source.startswith("rtsp://")
                self._set_seek_enabled(is_file)
                self._pipeline.start()

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

    def _on_video_info_ready(self, filename: str, w: int, h: int, fps: float) -> None:
        self._video_screen.set_video_info(filename, w, h, fps)

    # ── 모드 전환 ─────────────────────────────────────────────────────

    def _set_seek_enabled(self, enabled: bool) -> None:
        self._video_slider.setEnabled(enabled)
        self._btn_video_back.setEnabled(enabled)
        self._btn_video_forward.setEnabled(enabled)

    # ── 창 종료 처리 ──────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if self._pipeline.isRunning():
            self._pipeline.stop()
            self._pipeline.wait()
        super().closeEvent(event)


class VideoScreen(QWidget):
    """
    QPixmap을 받아 화면에 표시하는 단순 위젯.
    크기 변화에 맞춰 비율을 유지하며 스케일링한다.
    """

    def __init__(self):
        super().__init__()
        self._screen = self._make_screen()
        self._overlay = self._make_overlay()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._screen)
        self.setLayout(layout)

        self._overlay.setParent(self)
        self._overlay.move(5, 5)

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _make_screen(self) -> QLabel:
        screen = QLabel()
        screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen.setMinimumSize(640, 480)
        screen.setText("영상이 여기에 표시됩니다.")
        screen.setStyleSheet("""
            background:black; color:white;
            border:2px solid #444;
            font-size:16px; font-weight:bold;
        """)
        return screen

    def _make_overlay(self) -> QLabel:
        overlay = QLabel()
        overlay.setStyleSheet("""
            color:white; font-size:12px;
            background-color:rgba(0,0,0,128);
            padding:5px;
            border-radius:3px;
            border:none;
        """)
        overlay.hide()
        return overlay

    # ── public API ────────────────────────────────────────────────────

    def show_frame(self, pixmap: QPixmap) -> None:
        self._screen.setPixmap(pixmap.scaled(
            self._screen.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def set_video_info(self, filename: str, w: int, h: int, fps: float) -> None:
        self._overlay.setText(f"{filename}\n{w}x{h} @ {fps:.1f}fps")
        self._overlay.adjustSize()
        self._overlay.show()

    def clear_video_info(self) -> None:
        self._overlay.hide()


class SourceDialog(QDialog):
    """
    영상 소스 선택 다이얼로그.
    파일 또는 RTSP URL 을 선택할 수 있다.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 100)
        self.setWindowTitle("소스 불러오기")
        self.setStyleSheet("background-color:#1e1e1e; color:white;")
        self._result = None
        self._build_ui()

    # ── UI 구성 ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._url_input = self._make_url_input()
        self._btn_file = self._make_file_button()
        btn_box = self._make_button_box()

        body_layout = QHBoxLayout()
        body_layout.addWidget(self._url_input)
        body_layout.addWidget(self._btn_file)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.addLayout(body_layout)
        layout.addWidget(btn_box)

        self.setLayout(layout)  

    # ── 위젯 생성 ─────────────────────────────────────────────────────
    def _make_url_input(self) -> QLineEdit:
        url_input = QLineEdit()
        url_input.setPlaceholderText("RTSP URL 입력")
        url_input.setFixedHeight(30)
        url_input.setStyleSheet("""
            QLineEdit {
                background-color:#2a2a2a; color:white;
                border:1px solid #444; border-radius:5px;
                padding:5px; font-size:13px;
            }
        """)
        return url_input

    def _make_file_button(self) -> QPushButton:
        btn = QPushButton("파일 업로드")
        btn.setFixedHeight(30)
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; border:1px solid #444; padding:5px; }
            QPushButton:hover { background:#444; }
        """)
        btn.clicked.connect(self._on_file_clicked)
        return btn

    def _make_button_box(self) -> QPushButton:
        btn = QPushButton("확인")
        btn.setStyleSheet("""
            QPushButton { color:white; font-weight:bold; border-radius:5px; border:1px solid #444; padding:5px; }
            QPushButton:hover { background:#444; }
        """)
        btn.clicked.connect(self._on_ok)
        return btn

    # ── 이벤트 핸들러 ─────────────────────────────────────────────────

    def _on_file_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "비디오 파일 선택")
        if file_path:
            self._url_input.setText(file_path)

    def _on_ok(self) -> None:
        self._result = self._url_input.text()
        self.accept()

    # ── public API ────────────────────────────────────────────────────

    def get_source(self) -> str | None:
        return self._result