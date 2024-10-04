import unittest

import pandas as pd

from analysis import moving_average, differentiate, auto_correlation, find_extremes


class TestAnalysisMethods(unittest.TestCase):
    def setUp(self) -> None:
        """
        Инициализация данных для тестов.
        """
        self.data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_moving_average(self) -> None:
        """
        Тестирование функции вычисления скользящего среднего.
        """
        result = moving_average(self.data, window=3)
        self.assertEqual(result.iloc[2], 2)

    def test_differential(self) -> None:
        """
        Тестирование функции вычисления дифференциала.
        """
        result = differentiate(self.data)
        self.assertEqual(result.iloc[1], 1)

    def test_auto_correlation(self) -> None:
        """
        Тестирование функции автокорреляции.
        """
        result = auto_correlation(self.data)
        self.assertAlmostEqual(result, 1.0)

    def test_find_extremes(self) -> None:
        """
        Тестирование функции нахождения экстремумов.
        """
        result = find_extremes(self.data)
        self.assertTrue(result['maxima'].iloc[4])  # Пример максимума
        self.assertTrue(result['minima'].iloc[1])  # Пример минимума


if __name__ == '__main__':
    unittest.main()
