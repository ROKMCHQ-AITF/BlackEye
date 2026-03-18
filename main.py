import sys
from PyQt6.QtWidgets import QApplication
from app.pipeline import VideoPlaybackThread
from app.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(player=VideoPlaybackThread())
    window.show()
    sys.exit(app.exec())
