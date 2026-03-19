import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def start_gui():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())