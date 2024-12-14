import datetime
import logging
import threading
import time
from typing import Literal

from .data_fetcher import IDataFetcher, get_data_fetcher
from .database import Session, DataPointModel, MonitoringServiceModel
from .models import DataPoint, DataDomain

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self, domain: DataDomain, fetcher: IDataFetcher, keyword: str, interval: int):
        self.domain = domain
        self.fetcher = fetcher
        self.keyword = keyword
        self.interval = interval  # В секундах
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._running = False
        self._paused = False
        self._lock = threading.Lock()
        self.last_error = None

    def start(self):
        self._running = True
        self._thread.start()
        self.save_state()
        logger.info(f"Monitoring service for {self.keyword} started.")

    def _run(self):
        while self._running:
            with self._lock:
                if not self._paused:
                    retries = 3
                    for attempt in range(retries):
                        try:
                            start_time = datetime.datetime.now() - datetime.timedelta(seconds=self.interval)
                            end_time = datetime.datetime.now()
                            data = self.fetcher.fetch_data(self.keyword,
                                                           start_time,
                                                           end_time)
                            self._save_data(data)
                            self.last_error = None
                            break  # Успешно получили данные, выходим из цикла повторов
                        except Exception as e:
                            self.last_error = str(e)
                            logger.warning(
                                f"error while receiving data for {self.keyword} (попытка {attempt + 1}/{retries}): {e}")
                            time.sleep(5)  # Ожидание перед повторной попыткой
                    else:
                        logger.error(f"Не удалось получить данные для {self.keyword} после {retries} попыток.")
                self.save_state()
            time.sleep(self.interval)

    def _save_data(self, data: list[DataPoint]):
        session = Session()
        data_models = [
            DataPointModel(domain=self.domain.value,
                           keyword=self.keyword,
                           timestamp=dp.timestamp,
                           value=dp.value)
            for dp in data
        ]
        session.add_all(data_models)
        session.commit()
        session.close()

    def pause(self):
        with self._lock:
            self._paused = True
            self.save_state()
            logger.info(f"Monitoring service for {self.keyword} paused.")

    def resume(self):
        with self._lock:
            self._paused = False
            self.save_state()
            logger.info(f"Monitoring service for {self.keyword} resumed.")

    def stop(self):
        self._running = False
        self.save_state()
        logger.info(f"Monitoring service for {self.keyword} stopped.")

    def status(self) -> Literal["Running", "Paused", "Not Running"]:
        if self._running:
            return "Running" if not self._paused else "Paused"
        return "Not Running"

    def save_state(self):
        session = Session()
        service = session.query(MonitoringServiceModel).filter_by(keyword=self.keyword,
                                                                  domain=self.domain.value).first()
        if not service:
            service = MonitoringServiceModel(
                domain=self.domain.value,
                keyword=self.keyword,
                interval=self.interval,
                is_running=self._running and not self._paused,
                last_run=datetime.datetime.now()
            )
            session.add(service)
        else:
            service.interval = self.interval
            service.is_running = self._running and not self._paused
            service.last_run = datetime.datetime.now()
        session.commit()
        session.close()

    @staticmethod
    def load_services():
        session = Session()
        services_data = session.query(MonitoringServiceModel).all()
        session.close()
        services = []
        for service_data in services_data:
            domain = DataDomain(service_data.domain)
            fetcher = get_data_fetcher(domain)
            service = MonitoringService(domain, fetcher, service_data.keyword, service_data.interval)
            if service_data.is_running:
                service.start()
            else:
                service._paused = True
            services.append(service)
        return services
