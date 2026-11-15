
import ctypes
from ctypes import wintypes

from PySide6.QtCore import QObject, Signal


# ==================================
# Windows Events
# ==================================

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_SYSTEM_MINIMIZESTART = 0x0016
EVENT_SYSTEM_MINIMIZEEND = 0x0017

EVENT_OBJECT_DESTROY = 0x8001
EVENT_OBJECT_SHOW = 0x8002
EVENT_OBJECT_LOCATIONCHANGE = 0x800B

WINEVENT_OUTOFCONTEXT = 0x0000


# ==================================
# Windows API
# ==================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

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


# ==================================
# Window Tracker
# ==================================

class WindowTracker(QObject):

    window_event = Signal(int, int)

    def __init__(self):

        super().__init__()

        self.hooks = []
        self.callback = None

    # ----------------------------------
    # Start tracking
    # ----------------------------------

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

    # ----------------------------------
    # Stop tracking
    # ----------------------------------

    def stop(self):

        for hook in self.hooks:
            user32.UnhookWinEvent(hook)

        self.hooks.clear()
        self.callback = None

    # ----------------------------------
    # Event callback
    # ----------------------------------

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
