
import ctypes
import json

from pathlib import Path
from ctypes import wintypes

from PySide6.QtCore import (
    QCoreApplication,
    QAbstractNativeEventFilter,
)


# ==================================
# Windows API Setup
# ==================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000


class NativeMSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_ssize_t),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


user32.RegisterHotKey.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
    wintypes.UINT,
    wintypes.UINT,
]
user32.RegisterHotKey.restype = wintypes.BOOL

user32.UnregisterHotKey.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
]
user32.UnregisterHotKey.restype = wintypes.BOOL


# ==================================
# Key Definitions
# ==================================

MODIFIERS = {
    "ALT": MOD_ALT,
    "CTRL": MOD_CONTROL,
    "CONTROL": MOD_CONTROL,
    "SHIFT": MOD_SHIFT,
    "WIN": MOD_WIN,
    "WINDOWS": MOD_WIN,
}

KEYS = {
    "SPACE": 0x20,
    "TAB": 0x09,
    "ENTER": 0x0D,
    "ESC": 0x1B,
    "ESCAPE": 0x1B,
    "BACKSPACE": 0x08,
    "DELETE": 0x2E,
    "INSERT": 0x2D,
    "HOME": 0x24,
    "END": 0x23,
    "PAGEUP": 0x21,
    "PAGEDOWN": 0x22,

    "UP": 0x26,
    "DOWN": 0x28,
    "LEFT": 0x25,
    "RIGHT": 0x27,
}

# F1 through F24
for number in range(1, 25):
    KEYS[f"F{number}"] = 0x70 + number - 1

# Letters and numbers
for character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    KEYS[character] = ord(character)

for number in "0123456789":
    KEYS[number] = ord(number)


# ==================================
# Hotkey Manager
# ==================================

class HotkeyManager(QAbstractNativeEventFilter):

    def __init__(self, config_path=None):
        super().__init__()

        self.config_path = (
            Path(config_path)
            if config_path
            else Path(__file__).with_name("hotkeys.json")
        )

        self.app = QCoreApplication.instance()

        self.callbacks = {}
        self.registered_hotkeys = {}

        self.running = False

        self.load_config()

    # ----------------------------------
    # Configuration
    # ----------------------------------

    def load_config(self):
        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                self.config = json.load(file)

        except FileNotFoundError:
            print("[HOTKEY] Configuration file not found.")
            self.config = {}

        except json.JSONDecodeError as error:
            print(f"[HOTKEY] Invalid JSON configuration: {error}")
            self.config = {}

    # ----------------------------------
    # Callback Registration
    # ----------------------------------

    def bind(self, action, callback):
        """
        Connects an action from hotkeys.json
        to a function in the application.
        """

        self.callbacks[action] = callback

        if self.running:
            self._register_hotkeys()

    def unbind(self, action):
        self.callbacks.pop(action, None)

        if self.running:
            self._register_hotkeys()

    # ----------------------------------
    # Key Parsing
    # ----------------------------------

    @staticmethod
    def parse_hotkey(key_string):

        parts = [
            part.strip().upper()
            for part in key_string.split("+")
        ]

        modifiers = MOD_NOREPEAT
        virtual_key = None

        for part in parts:

            if part in MODIFIERS:
                modifiers |= MODIFIERS[part]

            elif part in KEYS:
                if virtual_key is not None:
                    raise ValueError("Multiple keys specified.")

                virtual_key = KEYS[part]

            else:
                raise ValueError(f"Unknown key: {part}")

        if virtual_key is None:
            raise ValueError("No key specified.")

        return modifiers, virtual_key

    # ----------------------------------
    # Starting / Stopping
    # ----------------------------------

    def start(self):

        if self.running:
            return

        if self.app is None:
            print("[HOTKEY] No Qt application instance found.")
            return

        self.app.installNativeEventFilter(self)

        self.app.aboutToQuit.connect(self.stop)

        self.running = True

        self._register_hotkeys()

        print("[HOTKEY] Manager started.")

    def stop(self):

        if not self.running:
            return

        for hotkey_id in list(self.registered_hotkeys):
            user32.UnregisterHotKey(None, hotkey_id)

        self.registered_hotkeys.clear()

        if self.app:
            self.app.removeNativeEventFilter(self)

        self.running = False

        print("[HOTKEY] Manager stopped.")

    # ----------------------------------
    # Windows Hotkey Registration
    # ----------------------------------

    def _register_hotkeys(self):

        # Unregister existing hotkeys first.
        for hotkey_id in list(self.registered_hotkeys):
            user32.UnregisterHotKey(None, hotkey_id)

        self.registered_hotkeys.clear()

        hotkey_id = 1

        for action, settings in self.config.items():

            if not settings.get("enabled", True):
                continue

            callback = self.callbacks.get(action)

            if callback is None:
                continue

            try:
                modifiers, virtual_key = self.parse_hotkey(
                    settings["key"]
                )

            except (ValueError, KeyError) as error:
                print(f"[HOTKEY] Invalid hotkey for {action}: {error}")
                continue

            success = user32.RegisterHotKey(
                None,
                hotkey_id,
                modifiers,
                virtual_key,
            )

            if success:
                self.registered_hotkeys[hotkey_id] = {
                    "action": action,
                    "callback": callback,
                }

                print(
                    f"[HOTKEY] Registered {settings['key']} "
                    f"for {action}."
                )

                hotkey_id += 1

            else:
                error = ctypes.get_last_error()

                print(
                    f"[HOTKEY] Failed to register "
                    f"{settings['key']} for {action}. "
                    f"Windows error: {error}"
                )

    # ----------------------------------
    # Windows Event Handling
    # ----------------------------------

    def nativeEventFilter(self, event_type, message):

        msg = ctypes.cast(
            int(message),
            ctypes.POINTER(NativeMSG),
        ).contents

        if msg.message == WM_HOTKEY:

            hotkey = self.registered_hotkeys.get(msg.wParam)

            if hotkey:
                try:
                    hotkey["callback"]()

                except Exception as error:
                    print(
                        f"[HOTKEY] Error executing "
                        f"{hotkey['action']}: {error}"
                    )

                return True, 0

        return False, 0
