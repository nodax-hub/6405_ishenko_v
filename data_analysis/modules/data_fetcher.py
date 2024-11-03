import logging
from datetime import datetime

import pandas as pd

from data_analysis.modules.data_domain import (DataDomain,
                                               DataStrategy,
                                               StockStrategy,
                                               WeatherStrategy,
                                               SearchTrendStrategy)

logger = logging.getLogger(__name__)


class DataFetcher:
    def __init__(self, domain: DataDomain):
        self.strategy = self._choose_strategy(domain)
        logger.info(f"Инициализация DataFetcher с доменом {domain}")

    def _choose_strategy(self, domain: DataDomain) -> DataStrategy:
        match domain:
            case DataDomain.STOCKS:
                return StockStrategy()
            case DataDomain.WEATHER:
                return WeatherStrategy()
            case DataDomain.SEARCH_TRENDS:
                return SearchTrendStrategy()
            case _:
                raise ValueError(f"Неизвестный домен данных: {domain}")

    def fetch_by_keyword(self, keyword: str,
                         start_date: datetime,
                         end_date: datetime = datetime.now()) -> pd.DataFrame:
        logger.info(f"Получение данных для домена {self.strategy.__class__.__name__}")
        return self.strategy.fetch_data(keyword, start_date, end_date)
