import unittest
from datetime import datetime, timedelta

from data_analysis.modules.data_domain import StockStrategy, WeatherStrategy, SearchTrendStrategy


class TestDataStrategies(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()

    def test_stock_strategy(self):
        strategy = StockStrategy()
        data = strategy.fetch_data("AAPL", self.start_date, self.end_date)
        self.assertIn('date', data.columns)
        self.assertIn('value', data.columns)
        print("Stock Strategy Data:\n", data.head())

    def test_weather_strategy(self):
        strategy = WeatherStrategy()
        data = strategy.fetch_data("Berlin", self.start_date, self.end_date)
        self.assertIn('date', data.columns)
        self.assertIn('value', data.columns)
        print("Weather Strategy Data:\n", data.head())

    def test_search_trend_strategy(self):
        strategy = SearchTrendStrategy()
        data = strategy.fetch_data("Python", self.start_date, self.end_date)
        self.assertIn('date', data.columns)
        self.assertIn('value', data.columns)
        print("Search Trend Strategy Data:\n", data.head())


if __name__ == "__main__":
    unittest.main()
