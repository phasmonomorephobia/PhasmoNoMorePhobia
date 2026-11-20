
from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QColor,
    QFontMetricsF,
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
        alignment=Qt.AlignmentFlag.AlignCenter,
        parent=None,
        shadow=False,
        shadow_color="#000000",
        shadow_blur=5,
        shadow_offset=(1, 2),
    ):
        super().__init__(text, parent)

        self.text_color = QColor(text_color)
        self.outline_color = QColor(outline_color)
        self.outline_width = outline_width

        self.setFont(
            QFont("Signika", font_size, font_weight)
        )
        self.setAlignment(alignment)

        # Leave room for the outline around the text
        margin = int(outline_width + 2)
        self.setContentsMargins(margin, margin, margin, margin)

        self.shadow = None
        if shadow:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setColor(QColor(shadow_color))
            self.shadow.setBlurRadius(shadow_blur)
            self.shadow.setOffset(*shadow_offset)
            self.setGraphicsEffect(self.shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        font = self.font()
        metrics = QFontMetricsF(font)

        text = self.text()
        bounds = metrics.tightBoundingRect(text)

        # Calculate horizontal position
        if self.alignment() & Qt.AlignmentFlag.AlignRight:
            x = self.width() - bounds.width() - bounds.left()
        elif self.alignment() & Qt.AlignmentFlag.AlignHCenter:
            x = (self.width() - bounds.width()) / 2 - bounds.left()
        else:
            x = -bounds.left()

        # Calculate vertical position
        if self.alignment() & Qt.AlignmentFlag.AlignBottom:
            y = self.height() - bounds.height() - bounds.top()
        elif self.alignment() & Qt.AlignmentFlag.AlignVCenter:
            y = (self.height() - bounds.height()) / 2 - bounds.top()
        else:
            y = -bounds.top()

        path = QPainterPath()
        path.addText(x, y, font, text)

        # Draw outline first
        pen = QPen(self.outline_color)
        pen.setWidthF(self.outline_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Draw text fill over the outline
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.text_color)
        painter.drawPath(path)

        painter.end()
