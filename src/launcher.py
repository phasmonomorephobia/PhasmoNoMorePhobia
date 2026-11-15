import sys
import psutil
import ctypes
import os
from ctypes import wintypes
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
)
from PySide6.QtGui import (
    QFont,
    QColor,
    QFontDatabase,
    QIcon,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QGridLayout,
)

from ui.outlined_label import OutlinedLabel
from settings import SettingsWindow


# ----------------------------------
# Asset paths
# ----------------------------------

ASSET_DIR = Path(__file__).resolve().parent / "assets"
IMAGE_DIR = ASSET_DIR / "images"
FONT_DIR = ASSET_DIR / "fonts"

# ----------------------------------
# Windows foreground window detection
# ----------------------------------

user32 = ctypes.windll.user32

user32.GetForegroundWindow.restype = wintypes.HWND

user32.GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD),
]

user32.GetWindowThreadProcessId.restype = wintypes.DWORD


# ----------------------------------
# Custom animated image button
# ----------------------------------

class HoverImageButton(QPushButton):
    def __init__(
        self,
        normal_size,
        hover_size,
        pressed_size=None,
        parent=None,
    ):
        super().__init__(parent)

        self.normal_size = QSize(*normal_size)
        self.hover_size = QSize(*hover_size)

        self.pressed_size = (
            QSize(*pressed_size)
            if pressed_size
            else QSize(
                max(1, normal_size[0] - 3),
                max(1, normal_size[1] - 3),
            )
        )

        self.animation = QPropertyAnimation(
            self,
            b"iconSize",
            self,
        )

        self.animation.setDuration(160)
        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.setIconSize(self.normal_size)

    def animate_icon(self, target_size):
        self.animation.stop()
        self.animation.setStartValue(self.iconSize())
        self.animation.setEndValue(target_size)
        self.animation.start()

    def enterEvent(self, event):
        self.animate_icon(self.hover_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_icon(self.normal_size)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.animate_icon(self.pressed_size)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.underMouse():
            self.animate_icon(self.hover_size)
        else:
            self.animate_icon(self.normal_size)


# ----------------------------------
# Font loading
# ----------------------------------

def load_fonts():
    normal_font = FONT_DIR / "Signika-Regular.ttf"
    bold_font = FONT_DIR / "Signika-Bold.ttf"

    for font_path in (normal_font, bold_font):
        font_id = QFontDatabase.addApplicationFont(
            str(font_path)
        )

        if font_id == -1:
            print(f"Failed to load font: {font_path}")
        else:
            print(f"Loaded font: {font_path.name}")


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


# ----------------------------------
# Main launcher window
# ----------------------------------

class MainWindow(QMainWindow):
    def __init__(self, overlay_manager):
        super().__init__()

        self.overlay_manager = overlay_manager
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
        minimize_button.setFont(
            QFont("Signika", 19, QFont.Weight.Normal)
        )
        minimize_button.setObjectName("minimizeButton")
        minimize_button.setFixedSize(14, 14)
        minimize_button.clicked.connect(self.showMinimized)

        add_shadow(
            minimize_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100,
        )

        close_button = QPushButton("X")
        close_button.setFont(
            QFont("Signika", 19, QFont.Weight.Normal)
        )
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(14, 14)
        close_button.clicked.connect(self.close)

        add_shadow(
            close_button,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100,
        )

        top_layout.addWidget(minimize_button)
        top_layout.addWidget(close_button)

        main_layout.addLayout(top_layout)

        # ----------------------------------
        # Application title
        # ----------------------------------

        main_layout.addSpacing(30)

        title = OutlinedLabel(
            text="PhasmoNoMorePhobia",
            font_size=19,
            font_weight=QFont.Weight.Bold,
            text_color="#FFFFFF",
            outline_color="#000000",
            outline_width=4,
        )

        add_shadow(
            title,
            blur=8,
            y_offset=4,
            color="#000000",
            opacity=200,
        )

        title.setContentsMargins(10, 10, 10, 10)
        title.setMinimumHeight(50)

        title.setStyleSheet("""
            color: white;
            background: transparent;
        """)

        main_layout.addWidget(title)

        # ----------------------------------
        # Launch button
        # ----------------------------------

        main_layout.addSpacing(20)

        self.launch_button = HoverImageButton(
            normal_size=(113, 71),
            hover_size=(119, 75),
            pressed_size=(109, 68),
        )

        launch_image = IMAGE_DIR / "launch_button.png"

        self.launch_button.setIcon(QIcon(str(launch_image)))
        self.launch_button.setIconSize(QSize(113, 71))
        self.launch_button.setFixedSize(123, 81)
        self.launch_button.setObjectName("launchButton")

        self.launch_button.clicked.connect(self.launch_game)

        self.launch_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }

            QPushButton:hover {
                background: transparent;
            }

            QPushButton:pressed {
                background: transparent;
            }
        """)

        add_shadow(
            self.launch_button,
            blur=8,
            y_offset=4,
            color="#000000",
            opacity=180,
        )

        launch_layout = QHBoxLayout()
        launch_layout.addStretch()
        launch_layout.addWidget(self.launch_button)
        launch_layout.addStretch()

        main_layout.addLayout(launch_layout)

        # ----------------------------------
        # View Mode label
        # ----------------------------------

        main_layout.addSpacing(30)

        view_label = OutlinedLabel(
            text="View Mode",
            font_size=13,
            font_weight=QFont.Weight.Normal,
            text_color="#FFFFFF",
            outline_color="#000000",
            outline_width=3,
        )

        add_shadow(
            view_label,
            blur=8,
            y_offset=2,
            color="#000000",
            opacity=100,
        )

        view_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            background: transparent;
        """)

        main_layout.addWidget(view_label)

        # ----------------------------------
        # View Mode dropdown
        # ----------------------------------

        main_layout.addSpacing(1.5)

        self.view_mode = QComboBox()
        self.view_mode.setObjectName("viewMode")
        self.view_mode.setFont(
            QFont("Signika", 19, QFont.Weight.Normal)
        )

        self.view_mode.addItems([
            "Simple",
            "Advanced",
            "Custom",
        ])

        add_shadow(
            self.view_mode,
            blur=8,
            y_offset=4,
            color="#000000",
            opacity=180,
        )

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

        bottom_layout = QGridLayout()
        bottom_layout.setColumnStretch(0, 1)
        bottom_layout.setColumnStretch(1, 1)
        bottom_layout.setColumnStretch(2, 1)

        self.status_label = QLabel("Waiting for Phasmophobia...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: white;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
            }
        """)

        self.game_check_timer = QTimer(self)
        self.game_check_timer.setInterval(50)
        self.game_check_timer.timeout.connect(self.check_game_status)
        self.game_check_timer.start()

        self.check_game_status()

        # Center the label across the entire window
        bottom_layout.addWidget(self.status_label, 0, 0, 1, 3)

        self.settings_button = HoverImageButton(
            normal_size=(42, 42),
            hover_size=(48, 48),
            pressed_size=(39, 39),
        )

        settings_image = IMAGE_DIR / "settings_button.png"

        self.settings_button.setIcon(QIcon(str(settings_image)))
        self.settings_button.setIconSize(QSize(42, 42))
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(50, 50)

        self.settings_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: "#BDBDBD";
                border: none;
                padding: 0px;
            }

            QPushButton:hover {
                background: transparent;
            }

            QPushButton:pressed {
                background: transparent;
            }
        """)

        self.settings_button.clicked.connect(self.open_settings)

        add_shadow(
            self.settings_button,
            blur=8,
            y_offset=4,
            color="#000000",
            opacity=180,
        )

        # Keep settings button in the bottom-right corner
        bottom_layout.addWidget(
            self.settings_button,
            0, 2,
            Qt.AlignmentFlag.AlignRight
        )

        main_layout.addLayout(bottom_layout)

        self.apply_styles()



    # ----------------------------------
    # Application actions
    # ----------------------------------


    def is_game_running(self):
        """Check whether Phasmophobia.exe is running."""

        for process in psutil.process_iter(["name"]):
            try:
                process_name = process.info["name"]

                if process_name and process_name.lower() == "phasmophobia.exe":
                    return True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    def check_game_status(self):
        """Update game status and manage launcher visibility."""

        game_running = self.is_game_running()

        if game_running:
            self.status_label.setText("Phasmophobia detected!")
        else:
            self.status_label.setText("Waiting for Phasmophobia...")
            if hasattr(self, "overlay"):
                self.overlay_manager.stop()

            self.launch_button.setIcon(QIcon(str(IMAGE_DIR / "launch_button.png")))

            return

        # Get the currently focused Windows window
        foreground_hwnd = user32.GetForegroundWindow()

        if not foreground_hwnd:
            return

        foreground_pid = wintypes.DWORD()

        user32.GetWindowThreadProcessId(
            foreground_hwnd,
            ctypes.byref(foreground_pid),
        )

        # Check whether Phasmophobia is focused
        if foreground_pid.value == 0:
            return

        if foreground_pid.value == os.getpid():
            # One of our application windows is focused.
            # Restore the launcher if it was minimized.
            if self.isMinimized():
                self.showNormal()

        else:
            # Check whether the game is focused
            try:
                foreground_process = psutil.Process(
                    foreground_pid.value
                ).name().lower()

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return

            if foreground_process == "phasmophobia.exe":
                if not self.isMinimized():
                    self.showMinimized()

    
    def launch_game(self):
        # Check whether Phasmophobia is running
        if not self.is_game_running():
            self.overlay_manager.stop()

            self.launch_button.setIcon(
                QIcon(str(IMAGE_DIR / "launch_button.png"))
            )

            self.status_label.setText("Waiting for Phasmophobia...")
            return

        # If the overlay is already running, close it
        if self.overlay_manager.running:
            self.overlay_manager.stop()

            self.launch_button.setIcon(
                QIcon(str(IMAGE_DIR / "launch_button.png"))
            )

            self.status_label.setText("Phasmophobia detected!")

        # Otherwise, start the overlay
        else:
            self.overlay_manager.start()

            self.launch_button.setIcon(
                QIcon(str(IMAGE_DIR / "close_button.png"))
            )

            self.status_label.setText("Overlay active")

    
    def closeEvent(self, event):
        self.overlay_manager.stop()
        super().closeEvent(event)

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

            QComboBox {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 3px 25px 3px 8px;
                font-family: "Signika";
                font-size: 10pt;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
            }

            QComboBox::down-arrow {
                image: url("assets/images/dropdown_arrow.svg");
                width: 16px;
                height: 16px;
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

            QComboBox#viewMode QAbstractItemView {
                background-color: #bdbdbd;
                color: black;
                selection-background-color: #999999;
                selection-color: black;
            }
        """)