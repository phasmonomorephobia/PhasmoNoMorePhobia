
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QPushButton


class KeybindButton(QPushButton):

    keyChanged = Signal(str)

    # Currently listening keybind button
    active_button = None

    def __init__(self, key="H", parent=None):
        super().__init__(parent)

        self.key = key
        self.listening = False

        self.setFixedSize(50, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setText(self.key)

        self.clicked.connect(self.start_listening)

    # ==================================
    # Start listening
    # ==================================

    def start_listening(self):

        # Cancel the previously active button
        if KeybindButton.active_button is not None:
            KeybindButton.active_button.stop_listening()

        # Make this button the active one
        KeybindButton.active_button = self

        self.listening = True
        self.setText("...")
        self.setFocus()

    # ==================================
    # Stop listening
    # ==================================

    def stop_listening(self):

        self.listening = False
        self.setText(self.key)

        if KeybindButton.active_button is self:
            KeybindButton.active_button = None

    # ==================================
    # Set keybind
    # ==================================

    def set_key(self, key):

        self.key = key
        self.setText(key if key else "---")

        self.keyChanged.emit(key)

    # ==================================
    # Capture keyboard input
    # ==================================

    def keyPressEvent(self, event):

        if not self.listening:
            super().keyPressEvent(event)
            return

        if event.isAutoRepeat():
            event.accept()
            return

        key = event.key()

        # ----------------------------------
        # Cancel
        # ----------------------------------

        if key == Qt.Key.Key_Escape:
            self.stop_listening()
            event.accept()
            return

        # ----------------------------------
        # Clear binding
        # ----------------------------------

        if key in (
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Delete,
        ):
            self.stop_listening()
            self.set_key("")
            event.accept()
            return

        # ----------------------------------
        # Ignore modifier-only presses
        # ----------------------------------

        if key in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            event.accept()
            return

        # ----------------------------------
        # Capture key combination
        # ----------------------------------

        modifiers = event.modifiers()

        sequence = QKeySequence(
            modifiers.value | key
        )

        key_name = sequence.toString(
            QKeySequence.SequenceFormat.NativeText
        )

        self.stop_listening()
        self.set_key(key_name)

        event.accept()
