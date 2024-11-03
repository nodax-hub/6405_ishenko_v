import unittest
from datetime import datetime
from data_analysis.modules.data_fetcher import DataFetcher
from data_analysis.modules.data_domain import DataDomain

class TestDataFetcher(unittest.TestCase):
    def test_fetch_stocks_data(self):
        fetcher = DataFetcher(DataDomain.STOCKS)
        df = fetcher.fetch_by_keyword("AAPL", datetime(2023, 1, 1), datetime(2023, 1, 10))
        self.assertFalse(df.empty)
        self.assertIn("value", df.columns)

    def test_fetch_weather_data(self):
        fetcher = DataFetcher(DataDomain.WEATHER)
        df = fetcher.fetch_by_keyword("Berlin", datetime(2023, 1, 1), datetime(2023, 1, 10))
        self.assertFalse(df.empty)
        self.assertIn("value", df.columns)

    def test_fetch_trend_data(self):
        fetcher = DataFetcher(DataDomain.SEARCH_TRENDS)
        df = fetcher.fetch_by_keyword("Python", datetime(2023, 1, 1), datetime(2023, 1, 10))
        self.assertFalse(df.empty)
        self.assertIn("value", df.columns)

if __name__ == "__main__":
    unittest.main()
