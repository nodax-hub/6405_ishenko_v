from abc import abstractmethod
from datetime import datetime
from typing import Protocol

import pandas as pd
import yfinance as yf
from geopy.geocoders import Nominatim
from meteostat import Daily, Point
from pytrends.request import TrendReq

from .models import DataPoint, DataDomain


class IDataFetcher(Protocol):
    @abstractmethod
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> list[DataPoint]:
        ...


def get_data_fetcher(domain: DataDomain) -> IDataFetcher:
    fetchers = {
        DataDomain.STOCKS: StockDataFetcher(),
        DataDomain.WEATHER: WeatherDataFetcher(),
        DataDomain.TRENDS: StockDataFetcher(),
    }
    if domain not in fetchers:
        raise ValueError(f"Unsupported data domain: {domain}")

    return fetchers[domain]


class StockDataFetcher:
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> list[DataPoint]:
        data = yf.download(keyword, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError(f"No data found for {keyword}")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row['Close'])
            for index, row in data.iterrows()
        ]
        return data_points


class WeatherDataFetcher:
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> list[DataPoint]:
        geolocator = Nominatim(user_agent="time_series_analyzer")
        location = geolocator.geocode(keyword)
        if location is None:
            raise ValueError(f"Не удалось найти координаты для города: {keyword}")

        point = Point(location.latitude, location.longitude)
        data = Daily(point, start_date, end_date)
        data = data.fetch()
        if data.empty:
            raise ValueError(f"No data found for {keyword} in the specified date range.")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row['tavg'])
            for index, row in data.iterrows()
            if not pd.isna(row['tavg'])
        ]
        return data_points


class TrendsDataFetcher:
    def fetch_data(self, keyword: str, start_date: datetime, end_date: datetime) -> list[DataPoint]:
        pytrends = TrendReq()
        timeframe = f'{start_date.strftime("%Y-%m-%d")} {end_date.strftime("%Y-%m-%d")}'
        pytrends.build_payload([keyword], timeframe=timeframe)
        data = pytrends.interest_over_time()
        if data.empty:
            raise ValueError(f"No data found for {keyword}")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row[keyword])
            for index, row in data.iterrows()
        ]
        return data_points
