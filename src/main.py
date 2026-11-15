import sys

from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QGraphicsDropShadowEffect,
)

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 180)

        self.setStyleSheet("""
            QDialog {
                background-color: #303030;
                color: white;
            }

            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        description = QLabel(
            "Settings will be added here."
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

def load_fonts():
    font_dir = (
        Path(__file__).resolve().parent
        / "assets"
        / "fonts"
    )

    Normal_font = font_dir / "Signika-Normal.ttf"
    bold_font = font_dir / "Signika-Bold.ttf"

    for font_path in (Normal_font, bold_font):
        font_id = QFontDatabase.addApplicationFont(
            str(font_path)
        )

        if font_id == -1:
            print(f"Failed to load font: {font_path}")
        else:
            print(f"Loaded font: {font_path.name}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.drag_position = None

        self.setWindowTitle("PhasmoNoMorePhobia")
        self.setFixedSize(335, 284)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.create_interface()

    def create_interface(self):

        # Main background
        self.container = QWidget()
        self.container.setObjectName("mainContainer")

        self.setCentralWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(0)

        # ----------------------------------
        # Top window controls
        # ----------------------------------

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.setSpacing(3)

        minimize_button = QPushButton("-")
        minimize_button.setFont(QFont("Signika", 19, QFont.Weight.Normal))
        minimize_button.setObjectName("minimizeButton")
        minimize_button.setFixedSize(14, 14)
        minimize_button.clicked.connect(self.showMinimized)

        close_button = QPushButton("X")
        close_button.setFont(QFont("Signika", 19, QFont.Weight.Normal))
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(14, 14)
        close_button.clicked.connect(self.close)

        top_layout.addWidget(minimize_button)
        top_layout.addWidget(close_button)

        main_layout.addLayout(top_layout)

        # ----------------------------------
        # Application title
        # ----------------------------------

        main_layout.addSpacing(38)

        title = QLabel("PhasmoNoMorePhobia")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setFont(QFont("Signika", 19, QFont.Weight.Bold))

        title.setStyleSheet("""
            color: white;
            background: transparent;
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 255))

        title.setGraphicsEffect(shadow)

        main_layout.addWidget(title)

        # ----------------------------------
        # Launch button
        # ----------------------------------

        main_layout.addSpacing(25)

        self.launch_button = QPushButton("LAUNCH")
        self.launch_button.setFont(QFont("Signika", 19, QFont.Weight.Bold))
        self.launch_button.setObjectName("launchButton")
        self.launch_button.setFixedSize(114, 60)

        self.launch_button.clicked.connect(self.launch_game)

        launch_layout = QHBoxLayout()
        launch_layout.addStretch()
        launch_layout.addWidget(self.launch_button)
        launch_layout.addStretch()

        main_layout.addLayout(launch_layout)

        # ----------------------------------
        # View Mode label
        # ----------------------------------

        main_layout.addSpacing(13)

        view_label = QLabel("View Mode")
        view_label.setFont(QFont("Signika", 19, QFont.Weight.Normal))
        view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        view_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            background: transparent;
        """)

        main_layout.addWidget(view_label)

        # ----------------------------------
        # View Mode dropdown
        # ----------------------------------

        main_layout.addSpacing(3)

        self.view_mode = QComboBox()
        self.view_mode.setObjectName("viewMode")
        self.view_mode.setFont(QFont("Signika", 19, QFont.Weight.Normal))
        self.view_mode.addItems([
            "Simple",
            "Advanced",
            "Custom"
        ])

        self.view_mode.setCurrentText("Simple")
        self.view_mode.setFixedSize(114, 23)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.addStretch()
        dropdown_layout.addWidget(self.view_mode)
        dropdown_layout.addStretch()

        main_layout.addLayout(dropdown_layout)

        # ----------------------------------
        # Bottom settings button
        # ----------------------------------

        main_layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(35, 35)
        self.settings_button.setFont(QFont("Signika", 19, QFont.Weight.Normal))

        self.settings_button.clicked.connect(
            self.open_settings
        )

        bottom_layout.addWidget(self.settings_button)

        main_layout.addLayout(bottom_layout)

        self.apply_styles()

    # ----------------------------------
    # Application actions
    # ----------------------------------
    def launch_game(self):
        mode = self.view_mode.currentText()

        print(f"Launch requested - View Mode: {mode}")

        # Game launching and overlay integration
        # will be implemented in a later stage.

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec()

    # ----------------------------------
    # Window dragging
    # ----------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 35:
                self.drag_position = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)

    # ----------------------------------
    # Application styling
    # ----------------------------------
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#mainContainer {
                background-color: #333333;
                border: 1px solid #222222;
                border-radius: 10px;
            }

            QPushButton#minimizeButton {
                background-color: #ff7900;
                color: #222222;
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }

            QPushButton#minimizeButton:hover {
                background-color: #ff9b36;
            }

            QPushButton#closeButton {
                background-color: #ff2525;
                color: #222222;
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }

            QPushButton#closeButton:hover {
                background-color: #ff5555;
            }

            QPushButton#launchButton {
                color: white;
                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #d000ff,
                    stop: 0.55 #a900ed,
                    stop: 1 #8500c9
                );

                border: 2px solid #e36bff;
                border-bottom: 6px solid #67009d;
                border-radius: 10px;

                padding-bottom: 3px;
            }

            QPushButton#launchButton:hover {
                background-color: #df24ff;
            }

            QPushButton#launchButton:pressed {
                background-color: #8500c9;
                border-bottom: 2px solid #67009d;
                padding-top: 4px;
            }

            QComboBox#viewMode {
                background-color: #bdbdbd;
                color: #111111;
                border: 1px solid #888888;
                border-radius: 3px;
                padding-left: 4px;
                font-size: 13px;
                font-weight: bold;
            }

            QComboBox#viewMode::drop-down {
                border: none;
                width: 22px;
            }

            QComboBox#viewMode QAbstractItemView {
                background-color: #bdbdbd;
                color: black;
                selection-background-color: #999999;
                selection-color: black;
            }

            QPushButton#settingsButton {
                background-color: #222222;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 0px;
            }

            QPushButton#settingsButton:hover {
                background-color: #444444;
                color: white;
            }

            QPushButton#settingsButton:pressed {
                background-color: #171717;
            }
        """)


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("PhasmoNoMorePhobia")

    load_fonts()

    app.setFont(QFont("Signika", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()