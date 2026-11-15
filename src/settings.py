from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
)


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 180)

        self.setStyleSheet("""
            QDialog {
                background-color: #303030;
                color: white;
            }

            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("Application Settings")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        description = QLabel(
            "Settings will be added here."
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()