from pathlib import Path
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QWidget,
)


class SettingsWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ==================================
        # Fonts
        # ==================================

        BASE_DIR = Path(__file__).resolve().parent.parent
        FONT_DIR = BASE_DIR / "assets" / "fonts"

        regular_font = FONT_DIR / "Signika-Regular.ttf"
        bold_font = FONT_DIR / "Signika-Bold.ttf"

        regular_id = QFontDatabase.addApplicationFont(str(regular_font))
        bold_id = QFontDatabase.addApplicationFont(str(bold_font))

        if regular_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(regular_id)[0]
            self.setFont(QFont(font_family, 10))
        else:
            print(f"[FONT ERROR] Could not load: {regular_font}")

        if bold_id == -1:
            print(f"[FONT ERROR] Could not load: {bold_font}")

        # ==================================
        # Window
        # ==================================

        self.setWindowTitle("Settings")
        self.setFixedSize(250, 347)
        self.drag_position = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QDialog {
                background-color: transparent
            }

            QLabel {
                color: white;
            }

            QPushButton {
                background-color: #dddddd;
                color: black;
                border: none;
                border-radius: 6px;
                font-size: 17px;
                font-weight: bold;
                font-family: "Signika";
            }

            QPushButton:hover {
                background-color: white;
            }
        """)

        # ==================================
        # Main Background
        # ==================================

        self.background = QWidget(self)
        self.background.setObjectName("background")

        self.background.setStyleSheet("""
            QWidget#background {
                background-color: #303030;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self.background)
        main_layout.setContentsMargins(10, 8, 10, 10)
        main_layout.setSpacing(9)

        self.background.setGeometry(self.rect())

        # ==================================
        # Header
        # ==================================

        self.header = QWidget()

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        self.title = QLabel("Settings")
        self.title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            font-family: "Signika";
        """)

        header_layout.addWidget(self.title)
        header_layout.addStretch()

        # ----------------------------------
        # Minimize button
        # ----------------------------------

        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(12, 12)

        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: #303030;
                border-radius: 6px;
                font-size: 10px;
                font-family: "Signika";
            }
        """)

        self.minimize_button.clicked.connect(self.showMinimized)

        # ----------------------------------
        # Close button
        # ----------------------------------

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(12, 12)

        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff2222;
                color: #303030;
                border-radius: 6px;
                font-size: 11px;
                font-family: "Signika";
            }
        """)

        self.close_button.clicked.connect(self.close)

        # ----------------------------------
        # Add buttons
        # ----------------------------------

        header_layout.addWidget(self.minimize_button)
        header_layout.addWidget(self.close_button)

        main_layout.addWidget(self.header)

        # ==================================
        # Setting Row Helper
        # ==================================

        def create_setting(title_text, description_text, control):

            row = QWidget()
            row_layout = QHBoxLayout(row)

            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)

            title_label = QLabel(title_text)
            title_label.setStyleSheet("""
                font-size: 17px;
                font-weight: bold;
                font-family: "Signika";
            """)

            description_label = QLabel(description_text)
            description_label.setStyleSheet("""
                font-size: 7px;
                font-family: "Signika";
                color: #bbbbbb;
            """)

            text_layout.addWidget(title_label)
            text_layout.addWidget(description_label)

            row_layout.addLayout(text_layout)
            row_layout.addStretch()
            row_layout.addWidget(control)

            return row

        # ==================================
        # Streamer Mode
        # ==================================

        self.streamer_mode = QCheckBox()
        self.streamer_mode.setChecked(True)
        self.streamer_mode.setFixedSize(46, 27)

        self.streamer_mode.setStyleSheet("""
            QCheckBox {
                background-color: #dddddd;
                border-radius: 6px;
            }

            QCheckBox::indicator {
                width: 23px;
                height: 23px;
                border-radius: 5px;
                background-color: #eeeeee;
            }

            QCheckBox::indicator:checked {
                background-color: #39ed45;
            }

            QCheckBox::indicator:unchecked {
                background-color: #eeeeee;
            }
        """)

        main_layout.addWidget(create_setting(
            "Streamer Mode",
            "*Hides the overlay in recordings or streams",
            self.streamer_mode
        ))

        # ==================================
        # Toggle Overlay
        # ==================================

        self.toggle_overlay_key = QPushButton("H")
        self.toggle_overlay_key.setFixedSize(50, 30)

        main_layout.addWidget(create_setting(
            "Toggle Overlay",
            "*This keybind will toggle the overlay when pressed",
            self.toggle_overlay_key
        ))

        # ==================================
        # Open Settings
        # ==================================

        self.open_settings_key = QPushButton("I")
        self.open_settings_key.setFixedSize(50, 30)

        main_layout.addWidget(create_setting(
            "Open Settings",
            "*This keybind opens this window when pressed",
            self.open_settings_key
        ))

        # ==================================
        # Open Game Settings
        # ==================================

        self.open_game_settings_key = QPushButton("O")
        self.open_game_settings_key.setFixedSize(50, 30)

        main_layout.addWidget(create_setting(
            "Open Game Settings",
            "*This keybind opens the Game Settings window",
            self.open_game_settings_key
        ))

        # ==================================
        # Game Settings Button
        # ==================================

        main_layout.addSpacing(1)

        self.game_settings_button = QPushButton("Game Settings")
        self.game_settings_button.setFixedSize(175, 34)

        self.game_settings_button.setStyleSheet("""
            QPushButton {
                background-color: #171717;
                color: white;
                border-radius: 5px;
                font-size: 19px;
                font-weight: bold;
                font-family: "Signika";
            }

            QPushButton:hover {
                background-color: #222222;
            }
        """)

        main_layout.addWidget(
            self.game_settings_button,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        main_layout.addStretch()
    
    # ==================================
    # Window dragging
    # ==================================

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

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

            event.accept()
            return

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None

        super().mouseReleaseEvent(event)
    
    def resizeEvent(self, event):
        self.background.setGeometry(self.rect())
        super().resizeEvent(event)
