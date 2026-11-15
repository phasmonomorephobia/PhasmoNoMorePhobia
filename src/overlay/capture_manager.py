
import ctypes
from ctypes import wintypes


# ==================================
# Windows API
# ==================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011

user32.SetWindowDisplayAffinity.argtypes = [
    wintypes.HWND,
    wintypes.DWORD,
]

user32.SetWindowDisplayAffinity.restype = wintypes.BOOL


# ==================================
# Capture Manager
# ==================================

class CaptureManager:

    def __init__(self, overlay, enabled=False):

        self.overlay = overlay
        self.enabled = bool(enabled)

    # ----------------------------------
    # Enable / Disable
    # ----------------------------------

    def set_enabled(self, enabled):

        previous_state = self.enabled
        self.enabled = bool(enabled)

        if self.apply():
            return True

        # Restore the previous state if Windows
        # rejected the change.
        self.enabled = previous_state

        return False

    # ----------------------------------
    # Apply display affinity
    # ----------------------------------

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
