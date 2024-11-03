import logging
import threading
import time
from datetime import datetime, timedelta

from data_analysis.modules.data_analyzer import DataAnalyzer
from data_analysis.modules.data_domain import DataDomain
from data_analysis.modules.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class DataMonitorService:
    def __init__(self, keyword: str, domain: DataDomain, interval: int = 60):
        self.keyword = keyword
        self.interval = interval
        self._running = False
        self.thread = None
        self.data_fetcher = DataFetcher(domain)
        self.data_analyzer = None

    def start(self):
        """Запускает мониторинг данных в отдельном потоке."""
        if not self._running:
            logger.info("Запуск DataMonitorService")
            self._running = True
            self.thread = threading.Thread(target=self._monitor, daemon=True)
            self.thread.start()

    def stop(self):
        """Останавливает мониторинг данных."""
        if self._running:
            logger.info("Остановка DataMonitorService")
            self._running = False
            if self.thread:
                self.thread.join()

    def _monitor(self):
        """Основная функция мониторинга, выполняемая в отдельном потоке."""
        while self._running:
            try:
                logger.info(f"Получение данных для '{self.keyword}'")
                data = self.data_fetcher.fetch_by_keyword(self.keyword, start_date=datetime.now() - timedelta(days=30))

                if not data.empty:
                    self.data_analyzer = DataAnalyzer(data)
                    trend_analysis = self.data_analyzer.analyze_trend_seasonality()
                    logger.info(f"Анализ тренда: {trend_analysis['trend'].iloc[-1]}")

                # Ждем заданный интервал перед следующим обновлением
                time.sleep(self.interval)

            except Exception as e:
                logger.error(f"Ошибка при мониторинге данных: {e}")

        logger.info("Мониторинг завершен")
