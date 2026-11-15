
import os
import ctypes
from ctypes import wintypes

import psutil

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)


# ==================================
# Windows API setup
# ==================================

HIDE_ON_UNFOCUS = True

user32 = ctypes.windll.user32

RECT = wintypes.RECT

user32.GetForegroundWindow.restype = wintypes.HWND

user32.GetWindowRect.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.RECT),
]
user32.GetWindowRect.restype = wintypes.BOOL

user32.GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD),
]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD

user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL


# ==================================
# Overlay window
# ==================================

class OverlayWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.launcher_pid = os.getpid()
        self.game_process_name = "Phasmophobia.exe"

        self.setWindowTitle("PhasmoNoMorePhobia Overlay")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        # ==================================
        # Temporary overlay content
        # ==================================

        self.status_label = QLabel(
            "PhasmoNoMorePhobia Overlay"
        )

        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(35, 35, 35, 220);
                border: 1px solid rgba(170, 70, 255, 180);
                border-radius: 8px;
                padding: 12px;
                font-family: "Signika";
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 0, 0)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        # ==================================
        # Focus detection timer
        # ==================================

        self.timer = QTimer(self)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.update_overlay)

        self.hide()

    # ==================================
    # Start and stop
    # ==================================

    def start(self):
        self.timer.start()
        self.update_overlay()

    def stop(self):
        self.timer.stop()
        self.hide()

    # ==================================
    # Windows process detection
    # ==================================

    def get_foreground_window(self):
        return user32.GetForegroundWindow()

    def get_window_process(self, hwnd):

        process_id = wintypes.DWORD()

        user32.GetWindowThreadProcessId(
            hwnd,
            ctypes.byref(process_id),
        )

        pid = process_id.value

        if not pid:
            return None, None

        try:
            process_name = psutil.Process(pid).name()
            return pid, process_name

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):
            return pid, None

    # ==================================
    # Window positioning
    # ==================================

    def get_window_geometry(self, hwnd):

        rect = RECT()

        success = user32.GetWindowRect(
            hwnd,
            ctypes.byref(rect),
        )

        if not success:
            return None

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if width <= 0 or height <= 0:
            return None

        return (
            rect.left,
            rect.top,
            width,
            height,
        )

    # ==================================
    # Overlay visibility
    # ==================================   
 
    def update_overlay(self):
        hwnd = self.get_foreground_window()

        if not hwnd:
            self.hide()
            return

        pid, process_name = self.get_window_process(hwnd)

        # Identify the focused application.
        is_game = (
            process_name is not None
            and process_name.lower() == self.game_process_name.lower()
        )

        is_launcher = (
            pid == self.launcher_pid
        )

        # ==================================
        # Phasmophobia is focused.
        # ==================================

        if is_game:

            if user32.IsIconic(hwnd):
                self.hide()
                return

            geometry = self.get_window_geometry(hwnd)

            if geometry is None:
                self.hide()
                return

            x, y, width, height = geometry

            self.setGeometry(x, y, width, height)

            if not self.isVisible():
                self.show()

            self.raise_()
            return

        # ==================================
        # PhasmoNoMorePhobia is focused.
        # ==================================

        if is_launcher:
            return

        # ==================================
        # Another application is focused.
        # ==================================

        if HIDE_ON_UNFOCUS:
            self.hide()

