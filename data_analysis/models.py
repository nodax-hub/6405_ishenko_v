from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass
class DataPoint:
    timestamp: datetime
    value: float


class DataDomain(StrEnum):
    STOCKS = 'Цены на акции'
    WEATHER = 'Погода'
    TRENDS = 'Поисковые тренды'
    FAKE_DATA = 'Фейковые данные'
