import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from launcher import MainWindow, load_fonts


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("PhasmoNoMorePhobia")

    load_fonts()
    app.setFont(QFont("Signika", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()