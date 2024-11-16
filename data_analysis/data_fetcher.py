import logging
import random
from abc import abstractmethod
import datetime
from typing import Protocol

import numpy as np
import pandas as pd
import yfinance as yf
from geopy.geocoders import Nominatim
from meteostat import Daily, Point
from pytrends.request import TrendReq

from .models import DataPoint, DataDomain

logger = logging.getLogger(__name__)


class IDataFetcher(Protocol):
    @abstractmethod
    def fetch_data(self, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime) -> list[DataPoint]:
        ...


def get_data_fetcher(domain: DataDomain) -> IDataFetcher:
    fetchers = {
        DataDomain.STOCKS: StockDataFetcher(),
        DataDomain.WEATHER: WeatherDataFetcher(),
        DataDomain.TRENDS: TrendsDataFetcher(),
        DataDomain.FAKE_DATA: FakeDataFetcher(),
    }
    if domain not in fetchers:
        raise ValueError(f"Unsupported data domain: {domain}")

    return fetchers[domain]


class FakeDataFetcher:
    def fetch_data(self, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime) -> list[DataPoint]:
        logger.info(f"Getting fake data for {keyword}")
        return [DataPoint(datetime.datetime.fromtimestamp(dt), random.randint(0, 20))
                for dt in np.linspace(start_time.timestamp(), end_time.timestamp())]


class StockDataFetcher:
    def fetch_data(self, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime) -> list[DataPoint]:
        logger.info(f"Getting stock data for {keyword}")
        data = yf.download(keyword, start=start_time, end=end_time, progress=False)
        if data.empty:
            raise ValueError(f"No data found for {keyword}")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row['Close'])
            for index, row in data.iterrows()
        ]
        logging.debug(f"Got data points for {keyword} from {start_time} to {end_time}: {data_points}")
        return data_points


class WeatherDataFetcher:
    def fetch_data(self, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime) -> list[DataPoint]:
        geolocator = Nominatim(user_agent="time_series_analyzer")
        location = geolocator.geocode(keyword)
        if location is None:
            raise ValueError(f"Не удалось найти координаты для города: {keyword}")

        logger.info(f"Getting weather data for {keyword} on {location}")
        point = Point(location.latitude, location.longitude)
        data = Daily(point, start_time, end_time)
        data = data.fetch()
        if data.empty:
            raise ValueError(f"No data found for {keyword} in the specified date range.")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row['tavg'])
            for index, row in data.iterrows()
            if not pd.isna(row['tavg'])
        ]
        logging.debug(f"Got data points for {keyword} from {start_time} to {end_time}: {data_points}")
        return data_points


class TrendsDataFetcher:
    def fetch_data(self, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime) -> list[DataPoint]:
        logger.info(f"Getting trends data for {keyword} on {start_time} to {end_time}")
        pytrends = TrendReq()
        timeframe = f'{start_time.strftime("%Y-%m-%d")} {end_time.strftime("%Y-%m-%d")}'
        pytrends.build_payload([keyword], timeframe=timeframe)
        data = pytrends.interest_over_time()
        if data.empty:
            raise ValueError(f"No data found for {keyword}")
        data_points = [
            DataPoint(timestamp=index.to_pydatetime(), value=row[keyword])
            for index, row in data.iterrows()
        ]
        logging.debug(f"Got data points for {keyword} from {start_time} to {end_time}: {data_points}")
        return data_points
