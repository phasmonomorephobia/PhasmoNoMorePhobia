
import ctypes
from ctypes import wintypes

import psutil


# ==================================
# Windows API
# ==================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

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


# ==================================
# Game Detector
# ==================================

class GameDetector:

    def __init__(self, process_name="Phasmophobia.exe"):

        self.game_process_name = process_name

    # ----------------------------------
    # Foreground window
    # ----------------------------------

    def get_foreground_window(self):

        return user32.GetForegroundWindow()

    # ----------------------------------
    # Process information
    # ----------------------------------

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

    # ----------------------------------
    # Game identification
    # ----------------------------------

    def is_game_window(self, hwnd):

        if not hwnd:
            return False

        _, process_name = self.get_window_process(hwnd)

        return (
            process_name is not None
            and process_name.lower()
            == self.game_process_name.lower()
        )

    # ----------------------------------
    # Window state
    # ----------------------------------

    @staticmethod
    def is_minimized(hwnd):

        return bool(user32.IsIconic(hwnd))

    @staticmethod
    def is_valid_window(hwnd):

        return bool(user32.IsWindow(hwnd))

    # ----------------------------------
    # Window geometry
    # ----------------------------------

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
