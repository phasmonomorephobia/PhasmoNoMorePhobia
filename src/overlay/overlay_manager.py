
from PySide6.QtCore import QObject, QTimer, QRect

from .overlay import OverlayWindow
from .window_tracker import (
    WindowTracker,
    EVENT_SYSTEM_FOREGROUND,
)
from .game_detector import GameDetector
from .capture_manager import CaptureManager


# ==================================
# Settings
# ==================================

HIDE_ON_UNFOCUS = True

STREAMER_MODE = False

GAME_PROCESS_NAME = "Phasmophobia.exe"


# ==================================
# Overlay Manager
# ==================================

class OverlayManager(QObject):

    def __init__(self):

        super().__init__()

        import os

        self.launcher_pid = os.getpid()

        self.running = False

        self.game_hwnd = None
        self.has_game_geometry = False

        self.update_pending = False

        # ----------------------------------
        # Create overlay UI
        # ----------------------------------

        self.overlay = OverlayWindow()

        # ----------------------------------
        # Game detection
        # ----------------------------------

        self.game_detector = GameDetector(
            GAME_PROCESS_NAME
        )

        # ----------------------------------
        # Window tracking
        # ----------------------------------

        self.window_tracker = WindowTracker()

        self.window_tracker.window_event.connect(
            self.handle_window_event
        )

        # ----------------------------------
        # Capture management
        # ----------------------------------

        self.capture_manager = CaptureManager(
            self.overlay,
            STREAMER_MODE,
        )

        # Reapply capture exclusion whenever
        # the overlay becomes visible.
        self.overlay.shown.connect(
            self.capture_manager.apply
        )

    # ==================================
    # START AND STOP
    # ==================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.window_tracker.start()

        # Create the native window handle and apply
        # capture exclusion before showing.
        self.overlay.winId()

        self.capture_manager.apply()

        # Initial game detection.
        self.update_overlay()

        print("[OVERLAY] Started")

    def stop(self):

        if not self.running:
            return

        self.running = False

        self.window_tracker.stop()

        self.overlay.hide()

        print("[OVERLAY] Stopped")

    # ==================================
    # WINDOWS EVENTS
    # ==================================

    def handle_window_event(self, event, hwnd):

        if not self.running:
            return

        # Ignore unrelated window movement events.
        if (
            event != EVENT_SYSTEM_FOREGROUND
            and hwnd != self.game_hwnd
        ):
            return

        # Avoid scheduling duplicate updates.
        if self.update_pending:
            return

        self.update_pending = True

        QTimer.singleShot(
            0,
            self.process_window_update,
        )

    def process_window_update(self):

        self.update_pending = False

        if self.running:
            self.update_overlay()

    # ==================================
    # OVERLAY VISIBILITY AND POSITIONING
    # ==================================

    def update_overlay(self):

        hwnd = self.game_detector.get_foreground_window()

        if not hwnd:
            self.overlay.hide()
            return

        pid, process_name = (
            self.game_detector.get_window_process(hwnd)
        )

        # ----------------------------------
        # Identify focused application
        # ----------------------------------

        is_game = (
            process_name is not None
            and process_name.lower()
            == GAME_PROCESS_NAME.lower()
        )

        is_launcher = (
            pid == self.launcher_pid
        )

        # ----------------------------------
        # Game focused
        # ----------------------------------

        if is_game:

            if self.game_detector.is_minimized(hwnd):
                self.overlay.hide()
                return

            geometry = (
                self.game_detector.get_window_geometry(hwnd)
            )

            if geometry is None:
                self.overlay.hide()
                return

            self.game_hwnd = int(hwnd)

            self.has_game_geometry = True

            x, y, width, height = geometry

            target_geometry = QRect(
                x,
                y,
                width,
                height,
            )

            if self.overlay.geometry() != target_geometry:

                self.overlay.setGeometry(
                    target_geometry
                )

            if not self.overlay.isVisible():
                self.overlay.show()

            self.overlay.raise_()

            return

        # ----------------------------------
        # Launcher focused
        # ----------------------------------

        if is_launcher:

            if not self.has_game_geometry:
                return

            if not self.overlay.isVisible():
                self.overlay.show()

            self.overlay.raise_()

            return

        # ----------------------------------
        # Another application focused
        # ----------------------------------

        if HIDE_ON_UNFOCUS:
            self.overlay.hide()

    # ==================================
    # STREAMER MODE
    # ==================================

    def set_streamer_mode(self, enabled):

        return self.capture_manager.set_enabled(
            enabled
        )

    def toggle_streamer_mode(self):

        enabled = not self.capture_manager.enabled

        success = self.set_streamer_mode(enabled)

        if success:

            print(
                f"[STREAMER MODE] "
                f"{'ENABLED' if enabled else 'DISABLED'}"
            )

        else:

            print(
                "[STREAMER MODE] Failed to change setting!"
            )
