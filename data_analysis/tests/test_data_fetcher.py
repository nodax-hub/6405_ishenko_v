import unittest
from datetime import datetime, timedelta

from data_analysis.data_fetcher import (
    StockDataFetcher, WeatherDataFetcher, TrendsDataFetcher
)


class TestDataFetcher(unittest.TestCase):
    def test_stock_data_fetcher(self):
        fetcher = StockDataFetcher()
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()
        data_points = fetcher.fetch_data('AAPL', start_date, end_date)
        self.assertTrue(len(data_points) > 0)

    def test_weather_data_fetcher(self):
        fetcher = WeatherDataFetcher()
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()
        data_points = fetcher.fetch_data('New York', start_date, end_date)
        self.assertTrue(len(data_points) > 0)

    def test_trends_data_fetcher(self):
        fetcher = TrendsDataFetcher()
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()
        data_points = fetcher.fetch_data('Python', start_date, end_date)
        self.assertTrue(len(data_points) > 0)


if __name__ == '__main__':
    unittest.main()
