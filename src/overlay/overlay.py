
from html import escape

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)


# ==================================
# Colors
# ==================================

WHITE = "#ffffff"
GREEN = "#00ff55"
RED = "#ff2020"


# ==================================
# Overlay Window
# ==================================

class OverlayWindow(QWidget):

    shown = Signal()

    def __init__(self):

        super().__init__()

        # ----------------------------------
        # Window configuration
        # ----------------------------------

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

        # ----------------------------------
        # Main layout
        # ----------------------------------

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(
            10, 16, 0, 0
        )

        self.main_layout.setSpacing(0)

        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        # Store value labels for future updates
        self.value_labels = {
            "player": {},
            "ghost": {},
            "round": {},
        }

        # ----------------------------------
        # Header
        # ----------------------------------

        self.title_label = QLabel(
            "PhasmoNoMorePhobia"
        )

        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Signika";
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.main_layout.addWidget(
            self.title_label
        )

        self.main_layout.addSpacing(10)

        self._add_divider()

        self.main_layout.addSpacing(12)

        # ----------------------------------
        # Player Section
        # ----------------------------------

        self._add_section(
            "Player",
            "player",
            [
                ("stamina", "Stamina:", [
                    ("100%", GREEN),
                    (" (Can/Can't Sprint/Infinite)", RED),
                ]),
                ("sanity", "Sanity:", [
                    ("100%", GREEN),
                    (" 75% 50% 25% (Frozen)", RED),
                ]),
                ("current_room", "Current Room:", [
                    ("Living Room", WHITE),
                ]),
                ("walk_speed", "Walk Speed:", [
                    ("1.6 m/s", WHITE),
                ]),
                ("sprint_speed", "Sprint Speed:", [
                    ("3 m/s", WHITE),
                ]),
                ("immortal", "Immortal:", [
                    ("No", RED),
                ]),
            ],
        )

        self.main_layout.addSpacing(12)

        self._add_divider()

        self.main_layout.addSpacing(14)

        # ----------------------------------
        # Ghost Section
        # ----------------------------------

        self._add_section(
            "Ghost",
            "ghost",
            [
                ("name", "Name:", [
                    ("Bob Alex", WHITE),
                ]),
                ("type", "Type:", [
                    ("Spirit", WHITE),
                ]),
                ("speed", "Speed:", [
                    ("1.7 m/s (Frozen)", WHITE),
                ]),
                ("frozen", "Frozen:", [
                    ("No", RED),
                ]),
                ("favorite_room", "Favorite Room:", [
                    ("Living Room", WHITE),
                ]),
                ("location", "Ghost Location:", [
                    ("Garage", WHITE),
                ]),
                ("harmless", "Harmless Ghost:", [
                    ("No", RED),
                ]),
                ("visible", "Visible Ghost:", [
                    ("No", RED),
                ]),
            ],
        )

        self.main_layout.addSpacing(12)

        self._add_divider()

        self.main_layout.addSpacing(14)

        # ----------------------------------
        # Round Section
        # ----------------------------------

        self._add_section(
            "Round",
            "round",
            [
                ("time", "Time:", [
                    ("00:01:01", WHITE),
                ]),
                ("difficulty", "Difficulty:", [
                    ("Professional", WHITE),
                ]),
                ("objectives", "Objectives:", [
                    ("Objective/Objective/Objective", RED),
                ]),
                ("breaker", "Breaker:", [
                    ("On", GREEN),
                    (" Off (Frozen)", RED),
                ]),
                ("setup_time", "Setup Phase Time:", [
                    ("00:00", WHITE),
                ]),
                ("infinite_salt", "Infinite Salt:", [
                    ("Yes", GREEN),
                ]),
                ("no_flashlight_flicker", "No Flashlight Flicker:", [
                    ("Yes", GREEN),
                ]),
            ],
        )

        # ----------------------------------
        # Finish
        # ----------------------------------

        self.main_layout.addStretch()

        self.hide()

    # ==================================
    # UI BUILDING HELPERS
    # ==================================

    def _add_divider(self):

        divider = QLabel()

        divider.setFixedSize(175, 3)

        divider.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 1px;
            }
        """)

        self.main_layout.addWidget(divider)

    def _add_section(self, title, section, rows):

        # Section heading

        heading = QLabel(title)

        heading.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Signika";
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.main_layout.addWidget(heading)

        self.main_layout.addSpacing(4)

        # Section rows

        for key, label_text, values in rows:

            row = QHBoxLayout()

            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)

            # Left-side label

            label = QLabel(label_text)

            label.setFixedWidth(82)

            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-family: "Signika";
                    font-size: 10px;
                    background: transparent;
                }
            """)

            # Right-side value

            value = QLabel()

            value.setTextFormat(
                Qt.TextFormat.RichText
            )

            value.setText(
                self._format_values(values)
            )

            value.setStyleSheet("""
                QLabel {
                    color: white;
                    font-family: "Signika";
                    font-size: 10px;
                    background: transparent;
                }
            """)

            value.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred
            )

            row.addWidget(label)
            row.addWidget(value, 1)

            self.main_layout.addLayout(row)

            self.value_labels[section][key] = value

        self.main_layout.addSpacing(2)

    # ==================================
    # VALUE FORMATTING
    # ==================================

    @staticmethod
    def _format_values(values):

        result = ""

        for text, color in values:

            result += (
                f'<span style="color:{color};">'
                f'{escape(str(text))}'
                f'</span>'
            )

        return result

    # ==================================
    # UI UPDATES
    # ==================================

    def set_value(
        self,
        section,
        key,
        value,
        color=WHITE,
    ):

        label = self.value_labels.get(
            section, {}
        ).get(key)

        if label is None:
            return

        label.setText(
            self._format_values([
                (str(value), color)
            ])
        )

    def set_rich_value(
        self,
        section,
        key,
        values,
    ):

        label = self.value_labels.get(
            section, {}
        ).get(key)

        if label is None:
            return

        label.setText(
            self._format_values(values)
        )

    # ----------------------------------
    # Existing status compatibility
    # ----------------------------------

    def set_status(self, text):

        self.title_label.setText(str(text))

    # ==================================
    # WINDOW LIFECYCLE
    # ==================================

    def showEvent(self, event):

        super().showEvent(event)

        self.shown.emit()
