import unittest
from datetime import datetime, timedelta

from data_analysis.data_analyzer import (
    moving_average, calculate_difference, autocorrelation, find_extrema
)
from data_analysis.models import DataPoint


class TestDataAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_points = [
            DataPoint(timestamp=datetime.now() - timedelta(days=i), value=i)
            for i in range(10)
        ]

    def test_moving_average(self):
        ma = moving_average(self.data_points, window_size=3)
        self.assertEqual(len(ma), len(self.data_points))
        self.assertIsNotNone(ma.iloc[2])  # Первые два значения должны быть NaN

    def test_calculate_difference(self):
        diff = calculate_difference(self.data_points)
        self.assertEqual(len(diff), len(self.data_points))
        self.assertIsNotNone(diff.iloc[1])  # Первое значение должно быть NaN

    def test_autocorrelation(self):
        ac = autocorrelation(self.data_points, lag=1)
        self.assertIsInstance(ac, float)

    def test_find_extrema(self):
        extrema = find_extrema(self.data_points)
        self.assertEqual(len(extrema), len(self.data_points))
        # Проверяем, что имеются экстремальные точки
        self.assertTrue(extrema['min'].isnull().all() or extrema['max'].isnull().all())


if __name__ == '__main__':
    unittest.main()
