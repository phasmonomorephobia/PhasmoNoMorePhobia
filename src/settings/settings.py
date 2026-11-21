from pathlib import Path
from ui.outlined_label import OutlinedLabel
from ui.toggle_switch import ToggleSwitch
from ui.keybind import KeybindButton
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFontDatabase, QFont, QColor
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QWidget,
    QGraphicsDropShadowEffect,
)

# ----------------------------------
# Drop shadow helper
# ----------------------------------

def add_shadow(
    widget,
    blur=8,
    x_offset=2,
    y_offset=4,
    color="#000000",
    opacity=180,
):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(x_offset, y_offset)

    shadow_color = QColor(color)
    shadow_color.setAlpha(opacity)
    shadow.setColor(shadow_color)

    widget.setGraphicsEffect(shadow)


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
        self.setFixedSize(270, 450)
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

        shadow = QGraphicsDropShadowEffect(self.background)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 0)
        self.background.setGraphicsEffect(shadow)

        self.background.setStyleSheet("""
            QWidget#background {
                background-color: #303030;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self.background)
        main_layout.setContentsMargins(10, 8, 10, 10)
        main_layout.setSpacing(9)

        self.background.setGeometry(self.rect().adjusted(10, 10, -10, -10))

        # ==================================
        # Header
        # ==================================

        self.header = QWidget()
        self.header.setFixedHeight(32)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        self.title = OutlinedLabel("Settings", 
        font_size=22, 
        outline_width=3, 
        alignment=Qt.AlignmentFlag.AlignLeft,
        shadow=True,
        shadow_blur=5,
        shadow_offset=(0,2),
        )
        self.title.setFixedHeight(32)
        self.title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            font-family: "Signika";
        """)

        header_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()

        # ----------------------------------
        # Minimize button
        # ----------------------------------

        self.minimize_button = QPushButton("-")
        self.minimize_button.setFixedSize(14, 14)

        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: #303030;
                border-radius: 6px;
                font-size: 13px;
                font-family: "Signika";
            }

            QPushButton:hover {
                background-color: #ff9b36;
            }
        """)
        add_shadow(
            self.minimize_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100,
            )

        self.minimize_button.clicked.connect(self.showMinimized)

        # ----------------------------------
        # Close button
        # ----------------------------------

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(14, 14)

        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff2222;
                color: #303030;
                border-radius: 6px;
                font-size: 13px;
                font-family: "Signika";
            }

            QPushButton:hover {
                background-color: #ff5555;
            }
        """)
        add_shadow(
            self.close_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100,
        )

        self.close_button.clicked.connect(self.close)

        # ----------------------------------
        # Add buttons
        # ----------------------------------

        main_layout.addWidget(self.header)

        # Individual button positioning
        self.minimize_button.setParent(self.header)
        self.close_button.setParent(self.header)

        self.minimize_button.move(198, 4)
        self.close_button.move(215, 4)

        # ==================================
        # Setting Row Helper
        # ==================================

        def create_setting(title_text, description_text, control, font_size=15, desc_font_size=13):

            row = QWidget()
            row_layout = QHBoxLayout(row)

            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)

            title_label = OutlinedLabel(
                title_text,
                font_size=font_size,
                outline_width=2,
                alignment=Qt.AlignmentFlag.AlignLeft,
                shadow=True,
                shadow_blur=5,
                shadow_offset=(0,2),
                )

            description_label = OutlinedLabel(
                description_text,
                font_size=desc_font_size,
                font_weight=QFont.Weight.Normal,
                text_color="#bbbbbb",
                outline_width=1.5,
                alignment=Qt.AlignmentFlag.AlignLeft,
                shadow=True,
                shadow_blur=5,
                shadow_offset=(0,2),
                )
            description_label.setStyleSheet("""
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

        self.streamer_mode = ToggleSwitch()
        self.streamer_mode.setChecked(False)

        main_layout.addWidget(create_setting(
            "Streamer Mode",
            "*Hides overlay in recordings",
            self.streamer_mode,
            desc_font_size=8.5,
        ))

        # ==================================
        # Toggle Overlay
        # ==================================

        self.hide_on_close = ToggleSwitch()
        self.hide_on_close.setChecked(False)

        main_layout.addWidget(create_setting(
            "Hide In Tray On Close",
            "*Launcher appears in tray when closed",
            self.hide_on_close,
            font_size=12.5,
            desc_font_size=6,
        ))

        # ==================================
        # Toggle Overlay
        # ==================================

        self.toggle_overlay_key = KeybindButton("H")

        main_layout.addWidget(create_setting(
            "Toggle Overlay",
            "*Toggles the overlay",
            self.toggle_overlay_key,
            desc_font_size=10
        ))

        # ==================================
        # Open Settings
        # ==================================

        self.open_settings_key = KeybindButton("I")

        main_layout.addWidget(create_setting(
            "Open Settings",
            "*Opens this window",
            self.open_settings_key,
            desc_font_size=10
        ))

        # ==================================
        # Open Game Settings
        # ==================================

        self.open_game_settings_key = KeybindButton("O")

        main_layout.addWidget(create_setting(
            "Open Game Settings",
            "*Opens Game Settings window",
            self.open_game_settings_key,
            font_size=13,
            desc_font_size=8
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

        add_shadow(
            self.game_settings_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100
        )

        main_layout.addWidget(
            self.game_settings_button,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # ==================================
        # Game Settings Button
        # ==================================

        main_layout.addSpacing(1)

        self.customize_view_button = QPushButton("Customize View")
        self.customize_view_button.setFixedSize(175, 34)

        self.customize_view_button.setStyleSheet("""
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

        add_shadow(
            self.customize_view_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100
        )

        main_layout.addWidget(
            self.customize_view_button,
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
        self.background.setGeometry(self.rect().adjusted(10, 10, -10, -10))
        super().resizeEvent(event)
