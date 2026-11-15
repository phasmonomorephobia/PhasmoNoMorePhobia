
import os
import ctypes
from ctypes import wintypes

import psutil

from PySide6.QtCore import (
    Qt,
    QObject,
    Signal,
    QTimer,
    QAbstractNativeEventFilter,
    QCoreApplication,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)
from PySide6.QtGui import QShortcut, QKeySequence


# ============================================================
# SETTINGS
# ============================================================

HIDE_ON_UNFOCUS = True

STREAMER_MODE = False

GAME_PROCESS_NAME = "Phasmophobia.exe"


# ============================================================
# WINDOWS API SETUP
# ============================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

# Window functions

user32.GetForegroundWindow.restype = wintypes.HWND

user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL

user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL

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


# Display affinity

WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011

user32.SetWindowDisplayAffinity.argtypes = [
    wintypes.HWND,
    wintypes.DWORD,
]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL


# WinEvent constants

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_SYSTEM_MINIMIZESTART = 0x0016
EVENT_SYSTEM_MINIMIZEEND = 0x0017

EVENT_OBJECT_DESTROY = 0x8001
EVENT_OBJECT_SHOW = 0x8002
EVENT_OBJECT_LOCATIONCHANGE = 0x800B

WINEVENT_OUTOFCONTEXT = 0x0000

WinEventProc = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD,
)

user32.SetWinEventHook.argtypes = [
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HMODULE,
    WinEventProc,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
]
user32.SetWinEventHook.restype = wintypes.HANDLE

user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
user32.UnhookWinEvent.restype = wintypes.BOOL


# ============================================================
# WINDOW TRACKER
# ============================================================

class WindowTracker(QObject):

    window_event = Signal(int, int)

    def __init__(self):
        super().__init__()

        self.hooks = []
        self.callback = None

    def start(self):

        if self.hooks:
            return

        events = [
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_MINIMIZESTART,
            EVENT_SYSTEM_MINIMIZEEND,
            EVENT_OBJECT_DESTROY,
            EVENT_OBJECT_SHOW,
            EVENT_OBJECT_LOCATIONCHANGE,
        ]

        self.callback = WinEventProc(
            self._event_callback
        )

        for event in events:

            hook = user32.SetWinEventHook(
                event,
                event,
                None,
                self.callback,
                0,
                0,
                WINEVENT_OUTOFCONTEXT,
            )

            if hook:
                self.hooks.append(hook)

            else:
                print(
                    f"[OVERLAY] Failed to install hook: "
                    f"{hex(event)} | "
                    f"{ctypes.get_last_error()}"
                )

    def stop(self):

        for hook in self.hooks:
            user32.UnhookWinEvent(hook)

        self.hooks.clear()
        self.callback = None

    def _event_callback(
        self,
        hook,
        event,
        hwnd,
        id_object,
        id_child,
        event_thread,
        event_time,
    ):

        self.window_event.emit(
            int(event),
            int(hwnd or 0),
        )


# ============================================================
# GAME DETECTOR
# ============================================================

class GameDetector:

    def __init__(self):

        self.game_process_name = GAME_PROCESS_NAME

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

    def is_game_window(self, hwnd):

        if not hwnd:
            return False

        pid, process_name = self.get_window_process(hwnd)

        return (
            process_name is not None
            and process_name.lower()
            == self.game_process_name.lower()
        )

    def get_window_geometry(self, hwnd):

        rect = wintypes.RECT()

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


# ============================================================
# CAPTURE MANAGER
# ============================================================

class CaptureManager:

    def __init__(self, overlay):

        self.overlay = overlay
        self.enabled = STREAMER_MODE

    def set_enabled(self, enabled):

        self.enabled = bool(enabled)

        return self.apply()

    def apply(self):

        hwnd = int(self.overlay.winId())

        affinity = (
            WDA_EXCLUDEFROMCAPTURE
            if self.enabled
            else WDA_NONE
        )

        success = user32.SetWindowDisplayAffinity(
            hwnd,
            affinity,
        )

        if not success:

            error = ctypes.get_last_error()

            print(
                f"[OVERLAY] Failed to apply display affinity: "
                f"{error}"
            )

            return False

        print(
            f"[OVERLAY] Streamer Mode: "
            f"{'ON' if self.enabled else 'OFF'}"
        )

        return True

# ==================================
# Global Hotkey
# ==================================

hotkey_user32 = ctypes.WinDLL("user32", use_last_error=True)

WM_HOTKEY = 0x0312
MOD_NOREPEAT = 0x4000

VK_F8 = 0x77
HOTKEY_ID = 1


class NativeMSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_ssize_t),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


hotkey_user32.RegisterHotKey.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
    wintypes.UINT,
    wintypes.UINT,
]
hotkey_user32.RegisterHotKey.restype = wintypes.BOOL

hotkey_user32.UnregisterHotKey.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
]
hotkey_user32.UnregisterHotKey.restype = wintypes.BOOL


class GlobalHotkey(QAbstractNativeEventFilter):

    def __init__(self, callback):
        super().__init__()

        self.callback = callback
        self.registered = False

        self.registered = bool(
            hotkey_user32.RegisterHotKey(
                None,
                HOTKEY_ID,
                MOD_NOREPEAT,
                VK_F8,
            )
        )

        if not self.registered:
            error = ctypes.get_last_error()
            print(f"[HOTKEY] Failed to register F8! Error: {error}")

    def nativeEventFilter(self, event_type, message):

        msg = ctypes.cast(
            int(message),
            ctypes.POINTER(NativeMSG),
        ).contents

        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
            self.callback()
            return True, 0

        return False, 0

    def unregister(self):

        if self.registered:
            hotkey_user32.UnregisterHotKey(None, HOTKEY_ID)
            self.registered = False
            print("[HOTKEY] F8 unregistered.")


# ============================================================
# OVERLAY WINDOW
# ============================================================

class OverlayWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.launcher_pid = os.getpid()

        self.game_detector = GameDetector()

        self.game_hwnd = None
        self.has_game_geometry = False

        self.running = False

        # ----------------------------------------------------
        # Window configuration
        # ----------------------------------------------------

        self.setWindowTitle(
            "PhasmoNoMorePhobia Overlay"
        )

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

        # ----------------------------------------------------
        # Overlay content
        # ----------------------------------------------------

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

        layout.setContentsMargins(
            20, 20, 0, 0
        )

        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        # ----------------------------------------------------
        # Window tracking
        # ----------------------------------------------------

        self.window_tracker = WindowTracker()

        self.window_tracker.window_event.connect(
            self.handle_window_event
        )

        # ----------------------------------------------------
        # Capture management
        # ----------------------------------------------------

        self.capture_manager = CaptureManager(self)

        # ==================================
        # Temporary Streamer Mode keybind
        # ==================================

        # Global F8 hotkey
        self.streamer_hotkey = GlobalHotkey(
            self.toggle_streamer_mode
        )

        app = QCoreApplication.instance()

        if self.streamer_hotkey.registered:
            app.installNativeEventFilter(self.streamer_hotkey)
            app.aboutToQuit.connect(self.streamer_hotkey.unregister)

            print("[HOTKEY] F8 registered globally.")

        # ----------------------------------------------------
        # Event update debounce
        # ----------------------------------------------------

        self.update_pending = False

        self.hide()

    # ========================================================
    # START AND STOP
    # ========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.window_tracker.start()

        # Apply capture exclusion before showing.
        self.capture_manager.apply()

        # Perform initial detection.
        self.update_overlay()

        print("[OVERLAY] Started")

    def stop(self):

        if not self.running:
            return

        self.running = False

        self.window_tracker.stop()

        self.hide()

        print("[OVERLAY] Stopped")

    # ========================================================
    # WINDOWS EVENTS
    # ========================================================

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

    # ========================================================
    # OVERLAY VISIBILITY
    # ========================================================

    def update_overlay(self):

        hwnd = self.game_detector.get_foreground_window()

        if not hwnd:
            self.hide()
            return

        pid, process_name = (
            self.game_detector.get_window_process(hwnd)
        )

        # ----------------------------------------------------
        # Identify focused application
        # ----------------------------------------------------

        is_game = (
            process_name is not None
            and process_name.lower()
            == GAME_PROCESS_NAME.lower()
        )

        is_launcher = (
            pid == self.launcher_pid
        )

        # ----------------------------------------------------
        # Game focused
        # ----------------------------------------------------

        if is_game:

            if user32.IsIconic(hwnd):
                self.hide()
                return

            geometry = (
                self.game_detector.get_window_geometry(hwnd)
            )

            if geometry is None:
                self.hide()
                return

            self.game_hwnd = int(hwnd)

            self.has_game_geometry = True

            x, y, width, height = geometry

            if self.geometry() != self.rect_from_geometry(
                x, y, width, height
            ):

                self.setGeometry(
                    x,
                    y,
                    width,
                    height,
                )

            if not self.isVisible():
                self.show()

            self.raise_()

            return

        # ----------------------------------------------------
        # Launcher focused
        # ----------------------------------------------------

        if is_launcher:

            if not self.has_game_geometry:
                return

            if not self.isVisible():
                self.show()

            self.raise_()

            return

        # ----------------------------------------------------
        # Another application focused
        # ----------------------------------------------------

        if HIDE_ON_UNFOCUS:
            self.hide()

    @staticmethod
    def rect_from_geometry(x, y, width, height):

        from PySide6.QtCore import QRect

        return QRect(
            x,
            y,
            width,
            height,
        )

    # ========================================================
    # STREAMER MODE
    # ========================================================

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
            print("[STREAMER MODE] Failed to change setting!")

    # ========================================================
    # WINDOW LIFECYCLE
    # ========================================================

    def showEvent(self, event):

        super().showEvent(event)

        # Reapply affinity if the native window handle
        # has been created or recreated.

        QTimer.singleShot(
            0,
            self.capture_manager.apply,
        )

    def closeEvent(self, event):

        self.stop()

        super().closeEvent(event)
