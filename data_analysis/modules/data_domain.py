from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum

import pandas as pd
import requests
from meteostat import Daily, Point
from pytrends.request import TrendReq
from yfinance import Ticker


class DataDomain(StrEnum):
    STOCKS = "Цены на акции"
    WEATHER = "Погода"
    SEARCH_TRENDS = "Поисковые тренды"


class DataStrategy(ABC):
    @abstractmethod
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Получить данные по ключевому слову за указанный период.

        :param keyword: Ключевое слово для поиска (например, тикер акции, город, поисковый запрос).
        :param start_date: Начальная дата для загрузки данных.
        :param end_date: Конечная дата для загрузки данных.
        :return: DataFrame с колонками 'date' и 'value'.
        """
        pass


class StockStrategy(DataStrategy):
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        ticker = Ticker(keyword)
        data = ticker.history(start=start_date, end=end_date)

        # Проверяем, что данные получены и приводим их к нужному формату
        if not data.empty:
            data = data[['Close']].rename(columns={'Close': 'value'}).reset_index()
            data = data[['Date', 'value']].rename(columns={'Date': 'date'})

        return data


class WeatherStrategy(DataStrategy):
    def get_coordinates(self, city: str) -> tuple:
        url = f"https://nominatim.openstreetmap.org/search"
        headers = {
            'User-Agent': 'MyDataAnalysisApp/1.0 (your_email@example.com)'
        }
        params = {
            'q': city,
            'format': 'json',
            'limit': 1
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Проверка успешности запроса
        data = response.json()

        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            raise ValueError(f"Не удалось найти координаты для города '{city}'")

    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        try:
            coordinates = self.get_coordinates(keyword)
            location = Point(*coordinates)
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении координат для '{keyword}': {e}")

        # Получаем данные о погоде
        data = Daily(location, start_date, end_date).fetch()

        # Проверка и форматирование данных
        if not data.empty:
            data = data[['tavg']].rename(columns={'tavg': 'value'}).reset_index()
            data = data[['time', 'value']].rename(columns={'time': 'date'})

        return data


class SearchTrendStrategy(DataStrategy):
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        pytrends = TrendReq()
        pytrends.build_payload([keyword],
                               timeframe=f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}")
        data = pytrends.interest_over_time()

        # Проверяем и форматируем данные
        if not data.empty:
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])
            data = data.rename(columns={keyword: 'value'}).reset_index()
            data = data[['date', 'value']]

        return data
