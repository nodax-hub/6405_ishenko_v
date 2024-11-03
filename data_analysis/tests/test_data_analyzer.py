import unittest
from datetime import datetime

import pandas as pd

from data_analysis.modules.data_analyzer import DataAnalyzer


class TestDataAnalyzer(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start=datetime(2023, 1, 1), periods=100)
        values = [i + (i % 10) for i in range(100)]
        self.data = pd.DataFrame({'date': dates, 'value': values})
        self.analyzer = DataAnalyzer(self.data)

    def test_calculate_moving_average(self):
        ma = self.analyzer.calculate_moving_average(5)
        self.assertEqual(len(ma), 100)

    def test_calculate_autocorrelation(self):
        ac = self.analyzer.calculate_autocorrelation(1)
        self.assertIsInstance(ac, float)

    def test_find_extremums(self):
        extremums = self.analyzer.find_extremums()
        self.assertIsInstance(extremums, list)

    def test_analyze_trend_seasonality(self):
        result = self.analyzer.analyze_trend_seasonality()
        self.assertIn("trend", result)
        self.assertIn("seasonality", result)


if __name__ == "__main__":
    unittest.main()
