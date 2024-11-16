import logging.config
import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    logging.info("Запуск приложения")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
