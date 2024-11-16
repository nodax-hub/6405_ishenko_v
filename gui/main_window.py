import logging
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QDateEdit, QCheckBox, QPushButton,
    QLabel, QMessageBox, QSpinBox, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from data_analysis.data_analyzer import (
    moving_average, find_extrema
)
from data_analysis.data_fetcher import get_data_fetcher
from data_analysis.database import get_data_points, Session, DataPointModel, MonitoringServiceModel
from data_analysis.models import DataDomain
from data_analysis.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.services_window = None
        self.setWindowTitle("Time Series Analyzer")
        self._services = []
        self._init_ui()
        self.load_monitoring_services()
        self.show_errors()

    def _init_ui(self):
        # Создание виджетов
        self.domain_combo = QComboBox()
        self.domain_combo.addItems(list(DataDomain))

        self.keyword_input = QLineEdit()
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-1))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())

        self.analyze_checkbox = QCheckBox("Анализировать данные")
        self.analyze_checkbox.stateChanged.connect(self.on_analyze_checkbox_changed)

        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(1)
        self.interval_input.setMaximum(86400)  # Максимум 24 часа
        self.interval_input.setValue(60)
        self.interval_input.setSuffix(" сек")

        self.view_data_button = QPushButton("Просмотреть данные")
        self.view_data_button.clicked.connect(self.view_data)

        self.start_monitoring_button = QPushButton("Запустить мониторинг")
        self.start_monitoring_button.clicked.connect(self.start_monitoring)

        # Создание лога ошибок
        self.error_log = QTextEdit()
        self.error_log.setReadOnly(True)
        self.error_log.setFixedHeight(int(self.height() * 0.1))  # Устанавливаем высоту ~10% от окна

        # Создание кнопки для скрытия/отображения лога ошибок
        self.toggle_error_log_button = QPushButton("Скрыть лог ошибок")
        self.toggle_error_log_button.clicked.connect(self.toggle_error_log)

        # Создание таблицы для отображения активных сервисов
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setMaximumWidth(550)
        self.services_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.services_table.setHorizontalHeaderLabels(["Домен", "Ключевое слово", "Статус", "Интервал", "Действия"])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.services_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Создание визуализации (графика)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Выберите домен данных:"))
        left_layout.addWidget(self.domain_combo)
        left_layout.addWidget(QLabel("Введите ключевое слово:"))
        left_layout.addWidget(self.keyword_input)
        left_layout.addWidget(QLabel("Интервал обновления (в секундах):"))
        left_layout.addWidget(self.interval_input)
        left_layout.addWidget(self.start_monitoring_button)

        left_layout.addWidget(QLabel("Визуализация данных:"))
        left_layout.addWidget(self.canvas)

        # Правая часть окна (таблица сервисов)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Активные мониторинговые сервисы:"))
        right_layout.addWidget(self.services_table)
        right_layout.addWidget(QLabel("Выберите период:"))
        right_layout.addWidget(self.start_date_edit)
        right_layout.addWidget(self.end_date_edit)
        right_layout.addWidget(self.analyze_checkbox)
        right_layout.addWidget(self.view_data_button)

        # Организация раскладки
        main_layout = QVBoxLayout()

        # Верхняя часть окна (управляющие элементы и отображение)
        upper_layout = QHBoxLayout()

        # Объединяем левую и правую части в верхней раскладке
        upper_layout.addLayout(left_layout)
        upper_layout.addLayout(right_layout)

        # Добавляем верхнюю раскладку в основную
        main_layout.addLayout(upper_layout)

        # Добавляем кнопку и лог ошибок в нижнюю часть окна
        error_log_layout = QVBoxLayout()
        error_log_layout.addWidget(self.error_log)
        error_log_layout.addWidget(self.toggle_error_log_button)

        main_layout.addLayout(error_log_layout)

        # Устанавливаем основной контейнер
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def view_data(self):
        selected_rows = self.services_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите сервис из таблицы.")
            return
        selected_row = selected_rows[0].row()
        selected_service = self._services[selected_row]

        domain = selected_service.domain
        keyword = selected_service.keyword
        analyze = self.analyze_checkbox.isChecked()
        # Используем даты из полей ввода
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        try:
            data_points = get_data_points(domain.value, keyword, start_date, end_date)
            if not data_points:
                QMessageBox.information(self, "Информация", "Нет данных для выбранного сервиса в указанном периоде.")
                return

            # Сохраняем данные для повторного использования
            self.current_data_points = data_points
            # Обновляем график
            self.update_graph(analyze)
        except Exception as e:
            logger.warning(f"Ошибка при просмотре данных: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
            self.error_log.append(str(e))

    def start_monitoring(self):
        domain = DataDomain(self.domain_combo.currentText())
        keyword = self.keyword_input.text()
        interval = self.interval_input.value()
        fetcher = get_data_fetcher(domain)
        service = MonitoringService(domain, fetcher, keyword, interval=interval)
        self._services.append(service)
        service.start()
        QMessageBox.information(self, "Мониторинг", f"Мониторинг для {keyword} запущен.")
        self.update_services_table()

    def update_services_table(self):
        self.services_table.setRowCount(len(self._services))
        for i, service in enumerate(self._services):
            domain_item = QTableWidgetItem(service.domain.value)
            keyword_item = QTableWidgetItem(service.keyword)
            status_item = QTableWidgetItem(service.status())
            interval_item = QTableWidgetItem(str(service.interval))

            # Кнопки действий
            action_layout = QHBoxLayout()
            action_widget = QWidget()

            action_button = QPushButton("Приостановить" if (service.status() == "Running") else "Возобновить")
            delete_button = QPushButton("Удалить")

            action_button.clicked.connect(partial(self.toggle_service, service))
            delete_button.clicked.connect(partial(self.delete_service, service))

            action_layout.addWidget(action_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)

            self.services_table.setItem(i, 0, domain_item)
            self.services_table.setItem(i, 1, keyword_item)
            self.services_table.setItem(i, 2, status_item)
            self.services_table.setItem(i, 3, interval_item)
            self.services_table.setCellWidget(i, 4, action_widget)

    def on_analyze_checkbox_changed(self):
        analyze = self.analyze_checkbox.isChecked()
        self.update_graph(analyze)

    def show_visualization(self, data_points, ma=None, diff=None, extrema=None):
        df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in data_points])
        df.set_index('timestamp', inplace=True)

        plt.figure(figsize=(10, 5))
        plt.plot(df['value'], label='Original Data')

        if ma is not None:
            plt.plot(ma, label='Moving Average')

        if extrema is not None:
            plt.scatter(extrema.index, extrema['min'], color='red', label='Minima')
            plt.scatter(extrema.index, extrema['max'], color='green', label='Maxima')

        plt.legend()
        plt.title('Data Visualization')
        plt.xlabel('Time')
        plt.ylabel('Value')

        # Отображение графика в новом окне
        fig = plt.gcf()
        canvas = FigureCanvas(fig)
        visualization_window = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        visualization_window.setLayout(layout)
        visualization_window.setWindowTitle('Data Visualization')
        visualization_window.show()

        # Сохраняем ссылку на окно, чтобы оно не было уничтожено
        self.visualization_windows.append(visualization_window)

    def _save_data_to_db(self, domain, keyword, data_points):
        session = Session()
        data_models = [
            DataPointModel(domain=domain.value, keyword=keyword, timestamp=dp.timestamp, value=dp.value)
            for dp in data_points
        ]
        session.add_all(data_models)
        session.commit()
        session.close()

    def load_monitoring_services(self):
        services = MonitoringService.load_services()
        self._services.extend(services)
        # Убираем повторный запуск сервисов
        # for service in self._services:
        #     if service.status() == "Running":
        #         service.start()
        self.update_services_table()

    def show_errors(self):
        handler = logging.StreamHandler(self)
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def write(self, message):
        self.error_log.append(message)

    def flush(self):
        pass

    def update_graph(self, analyze):
        if not hasattr(self, 'current_data_points') or not self.current_data_points:
            return
        df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in self.current_data_points])
        df.set_index('timestamp', inplace=True)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(df['value'], label='Original Data')

        if analyze:
            ma = moving_average(self.current_data_points, window_size=5)
            extrema = find_extrema(self.current_data_points)
            ax.plot(ma, label='Moving Average')
            if not extrema['min'].isnull().all():
                ax.scatter(extrema.index, extrema['min'], color='red', label='Minima')
            if not extrema['max'].isnull().all():
                ax.scatter(extrema.index, extrema['max'], color='green', label='Maxima')

        ax.legend()
        ax.set_title('Data Visualization')
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        self.canvas.draw()

    def toggle_error_log(self):
        if self.error_log.isVisible():
            self.error_log.hide()
            self.toggle_error_log_button.setText("Показать лог ошибок")
        else:
            self.error_log.show()
            self.toggle_error_log_button.setText("Скрыть лог ошибок")

    def toggle_service(self, service):
        if service.status() == "Running":
            service.pause()
        else:
            if service.status() == "Paused":
                service.resume()
            else:
                service.start()

        self.update_services_table()

    def delete_service(self, service):
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f"Вы уверены, что хотите удалить сервис для {service.keyword} и все связанные данные?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Останавливаем сервис, если он запущен
        service.stop()
        # Удаляем сервис из списка
        self._services.remove(service)
        # Удаляем записи из базы данных
        session = Session()
        # Удаляем записи DataPointModel
        session.query(DataPointModel).filter_by(
            domain=service.domain.value, keyword=service.keyword
        ).delete()
        # Удаляем запись MonitoringServiceModel
        session.query(MonitoringServiceModel).filter_by(
            domain=service.domain.value, keyword=service.keyword
        ).delete()
        session.commit()
        session.close()
        # Обновляем таблицу
        self.update_services_table()
        QMessageBox.information(self, "Удаление завершено",
                                f"Сервис для {service.keyword} и все связанные данные удалены.")
