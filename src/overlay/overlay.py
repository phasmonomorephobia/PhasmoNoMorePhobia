
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)


class OverlayWindow(QWidget):

    shown = Signal()

    def __init__(self):

        super().__init__()

        # ----------------------------------
        # Window configuration
        # ----------------------------------

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

        # ----------------------------------
        # Overlay content
        # ----------------------------------

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

        self.hide()

    # ----------------------------------
    # UI updates
    # ----------------------------------

    def set_status(self, text):

        self.status_label.setText(text)

    # ----------------------------------
    # Window lifecycle
    # ----------------------------------

    def showEvent(self, event):

        super().showEvent(event)

        self.shown.emit()
