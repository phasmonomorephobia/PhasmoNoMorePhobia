
import sys

from PySide6.QtWidgets import QApplication

from launcher import MainWindow, load_fonts
from overlay import OverlayManager
from hotkeys import HotkeyManager


app = QApplication(sys.argv)

# Load font
load_fonts()

# ----------------------------------
# Create managers
# ----------------------------------

overlay_manager = OverlayManager()
hotkey_manager = HotkeyManager()

# ----------------------------------
# Connect global hotkeys
# ----------------------------------
launcher = MainWindow(overlay_manager)

hotkey_manager.bind(
    "toggle_streamer_mode",
    overlay_manager.toggle_streamer_mode,
)

hotkey_manager.bind(
    "toggle_overlay",
    launcher.toggle_overlay,
)

# ----------------------------------
# Create launcher
# ----------------------------------
launcher.show()

# ----------------------------------
# Start global hotkeys
# ----------------------------------

hotkey_manager.start()

# ----------------------------------
# Cleanup
# ----------------------------------

app.aboutToQuit.connect(overlay_manager.stop)
app.aboutToQuit.connect(hotkey_manager.stop)

sys.exit(app.exec())
