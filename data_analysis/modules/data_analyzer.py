from typing import List, Dict, Any

import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import medfilt


class DataAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def calculate_moving_average(self, window_size: int) -> pd.Series:
        """Рассчитывает скользящее среднее."""
        return self.data['value'].rolling(window=window_size).mean()

    def calculate_median_filter(self, kernel_size: int) -> pd.Series:
        """Применяет медианный фильтр."""
        return pd.Series(medfilt(self.data['value'], kernel_size=kernel_size))

    def calculate_differential(self) -> pd.Series:
        """Рассчитывает дифференциал временного ряда."""
        return self.data['value'].diff()

    def calculate_autocorrelation(self, lag: int) -> float:
        """Рассчитывает автокорреляцию с заданным лагом."""
        return self.data['value'].autocorr(lag=lag)

    def find_extremums(self) -> List[int]:
        """Находит индексы локальных экстремумов."""
        diff = self.data['value'].diff()
        extremums = diff[(diff.shift(1) * diff < 0)].index.tolist()
        return extremums

    def analyze_trend_seasonality(self) -> Dict[str, Any]:
        """Анализирует тренды и сезонность данных."""
        # Простая демонстрация для примера
        trend = self.calculate_moving_average(12)
        seasonal = self.calculate_moving_average(6) - trend
        return {
            "trend": trend,
            "seasonality": seasonal
        }

    def analyze_trend(self, window_size: int = 5, kernel_size: int = 5, lag: int = 1) -> None:
        """Проводит анализ тренда и отображает графики."""

        # Вычисления
        moving_average = self.calculate_moving_average(window_size)
        median_filter = self.calculate_median_filter(kernel_size)
        differential = self.calculate_differential()
        autocorrelation = self.calculate_autocorrelation(lag)
        extremums = self.find_extremums()

        # Вывод значений автокорреляции
        print(f"Автокорреляция с лагом {lag}: {autocorrelation}")

        # Построение графика
        plt.figure(figsize=(12, 8))

        # Основной график данных
        plt.plot(self.data['date'], self.data['value'], label="Original Data", color="blue")
        plt.plot(self.data['date'], moving_average, label=f"Moving Average (window={window_size})", color="orange")
        plt.plot(self.data['date'], median_filter, label=f"Median Filter (kernel={kernel_size})", color="green")

        # Дифференциал
        plt.plot(self.data['date'], differential, label="Differential", linestyle="--", color="purple")

        # Отметка экстремумов
        plt.scatter(self.data['date'].iloc[extremums], self.data['value'].iloc[extremums], color="red",
                    label="Extremums", zorder=5)

        # Настройка и оформление графика
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Trend Analysis with Moving Average, Median Filter, Differential, and Extremums")
        plt.legend()
        plt.grid(True)

        # Показ графика
        plt.show()
