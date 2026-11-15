
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QColor,
    QFont,
)
from PySide6.QtCore import Qt


class OutlinedLabel(QLabel):

    def __init__(
        self,
        text="",
        font_size=19,
        font_weight=QFont.Weight.Bold,
        text_color="#FFFFFF",
        outline_color="#000000",
        outline_width=2,
        parent=None
    ):
        super().__init__(text, parent)

        self.font_size = font_size
        self.font_weight = font_weight
        self.text_color = QColor(text_color)
        self.outline_color = QColor(outline_color)
        self.outline_width = outline_width

        self.setFont(
            QFont("Signika", font_size, font_weight)
        )

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing
        )

        font = self.font()
        metrics = painter.fontMetrics()

        text_width = metrics.horizontalAdvance(self.text())
        text_height = metrics.ascent()

        x = (self.width() - text_width) / 2
        y = (
            self.height()
            + text_height
            - metrics.height()
        ) / 2 + metrics.ascent()

        path = QPainterPath()

        path.addText(x, y, font, self.text())

        # Draw outline
        pen = QPen(self.outline_color)
        pen.setWidthF(self.outline_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Draw text fill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.text_color)
        painter.drawPath(path)

        painter.end()
