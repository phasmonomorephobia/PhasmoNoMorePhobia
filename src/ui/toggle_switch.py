
from PySide6.QtCore import (
    Qt,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QVariantAnimation,
)
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(53, 32.33)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._offset = 0.0

        self.animation = QPropertyAnimation(self, b"offset", self)
        self.animation.setDuration(180)
        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self._track_color = QColor("#ff001b")

        self.color_animation = QVariantAnimation(self)
        self.color_animation.setDuration(200)
        self.color_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        self.color_animation.valueChanged.connect(
            self.set_track_color
        )

        self.toggled.connect(self.animate_toggle)

    # ----------------------------------
    # Animation property
    # ----------------------------------

    def get_offset(self):
        return self._offset

    def set_offset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, get_offset, set_offset)

    # ----------------------------------
    # Toggle animation
    # ----------------------------------

    def animate_toggle(self, checked):

        self.animation.stop()

        self.animation.setStartValue(self._offset)
        self.animation.setEndValue(1.0 if checked else 0.0)

        self.animation.start()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self.isChecked())
            event.accept()
            return

        super().mousePressEvent(event)
    
    def set_track_color(self, color):
        self._track_color = color
        self.update()


    def animate_toggle(self, checked):

        # Knob animation
        self.animation.stop()
        self.animation.setStartValue(self._offset)
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animation.start()

        # Color animation
        self.color_animation.stop()
        self.color_animation.setStartValue(self._track_color)
        self.color_animation.setEndValue(
            QColor("#20f33b") if checked else QColor("#ff001b")
        )
        self.color_animation.start()

    # ----------------------------------
    # Drawing
    # ----------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        knob_width = 26
        knob_height = height

        # ----------------------------------
        # Background track
        # ----------------------------------

        track_color = (
            self._track_color
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)

        painter.drawRoundedRect(
            0,
            0,
            width,
            height,
            8,
            8,
        )

        # ----------------------------------
        # Moving knob
        # ----------------------------------

        max_offset = width - knob_width

        knob_x = self._offset * max_offset

        knob_rect = (
            knob_x,
            0,
            knob_width,
            knob_height,
        )

        # ----------------------------------
        # Knob shadow
        # ----------------------------------

        for i in range(6, 0, -1):

            alpha = int(9 + (6 - i) * 5)

            shadow_color = QColor(0, 0, 0, alpha)

            painter.setBrush(shadow_color)

            painter.drawRoundedRect(
                knob_x - i / 2,
                -i / 2,
                knob_width + i,
                knob_height + i,
                13 + i / 2,
                13 + i / 2,
            )

        # ----------------------------------
        # Knob
        # ----------------------------------

        painter.setBrush(QColor("#dddddd"))

        painter.drawRoundedRect(
            *knob_rect,
            8,
            8,
        )

        painter.end()
