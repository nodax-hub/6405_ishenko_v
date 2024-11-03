import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, \
    QStatusBar

from data_analysis.modules.data_domain import DataDomain
from data_analysis.modules.data_monitor_service import DataMonitorService


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analysis Tool")
        self.setGeometry(100, 100, 400, 200)
        self.data_monitor_service = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Выпадающий список для выбора домена данных
        self.domain_select = QComboBox()
        self.domain_select.addItems([domain.value for domain in DataDomain])
        layout.addWidget(self.domain_select)

        # Поле ввода для ключевого слова
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Введите ключевое слово")
        layout.addWidget(self.keyword_input)

        # Кнопки для управления мониторингом
        self.start_button = QPushButton("Запустить мониторинг")
        self.start_button.clicked.connect(self.start_monitoring)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Остановить мониторинг")
        self.stop_button.clicked.connect(self.stop_monitoring)
        layout.addWidget(self.stop_button)

        # Настраиваем центральный виджет
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Устанавливаем статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Статус: Ожидание")

    def start_monitoring(self):
        keyword = self.keyword_input.text()
        selected_domain = DataDomain(self.domain_select.currentText())

        if keyword:
            self.data_monitor_service = DataMonitorService(keyword=keyword, domain=selected_domain, interval=10)
            self.data_monitor_service.start()
            self.status_bar.showMessage("Статус: Мониторинг запущен")
        else:
            self.status_bar.showMessage("Статус: Введите ключевое слово")

    def stop_monitoring(self):
        if self.data_monitor_service:
            self.data_monitor_service.stop()
            self.status_bar.showMessage("Статус: Мониторинг остановлен")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
