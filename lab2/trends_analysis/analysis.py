from typing import List

import pandas as pd
from pytrends.request import TrendReq

# Отключаем предупреждение
pd.set_option('future.no_silent_downcasting', True)


def get_trend_data(keywords: List[str], timeframe: str = 'today 5-y') -> pd.DataFrame:
    """
    Получает данные о трендах для указанных ключевых слов с помощью библиотеки pytrends.

    :param keywords: Список ключевых слов для поиска трендов.
    :param timeframe: Временной промежуток для получения данных (по умолчанию 5 лет).
    :return: DataFrame с временным рядом трендов.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='', gprop='')

    # Получение данных о трендах
    data = pytrends.interest_over_time()

    # Преобразование типов данных для устранения предупреждений
    data = data.infer_objects(copy=False)

    # Удаление столбца 'isPartial', если он существует
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])

    return data


def save_to_excel(data: pd.DataFrame, filename: str) -> None:
    """
    Сохраняет данные в Excel файл.

    :param data: DataFrame с данными для сохранения.
    :param filename: Имя файла для сохранения.
    """
    data.to_excel(filename, sheet_name='Trends')
    print(f"Data saved to {filename}")


def moving_average(data: pd.Series, window: int = 12) -> pd.Series:
    """
    Вычисляет скользящее среднее по временным данным.

    :param data: Временной ряд в виде Series.
    :param window: Размер окна для скользящего среднего (по умолчанию 12).
    :return: Series с результатами вычисления.
    """
    return data.rolling(window=window).mean()


def moving_average_manual(data: pd.Series, window: int = 12) -> pd.Series:
    return pd.Series(data=[sum(data[max(0, i - window):i].values) / window for i in range(len(data))],
                     index=data.index)


def differentiate(data: pd.Series) -> pd.Series:
    """
    Вычисляет дифференциал временного ряда.

    :param data: Временной ряд в виде Series.
    :return: Series с результатами вычисления.
    """
    return data.diff()


def auto_correlation(data: pd.Series, lag: int = 1) -> float:
    """
    Вычисляет автокорреляцию временного ряда.

    :param data: Временной ряд в виде Series.
    :param lag: Задержка для вычисления автокорреляции (по умолчанию 1).
    :return: Значение автокорреляции.
    """
    return data.autocorr(lag=lag)


def find_extremes(data: pd.Series) -> pd.DataFrame:
    """
    Находит точки экстремума (максимумы и минимумы) во временном ряду.

    :param data: Временной ряд в виде Series.
    :return: DataFrame с точками максимумов и минимумов.
    """
    maxima = (data.shift(1) < data) & (data.shift(-1) < data)
    minima = (data.shift(1) > data) & (data.shift(-1) > data)
    return pd.DataFrame({'maxima': maxima, 'minima': minima})


def analyze_trend_and_save(data: pd.DataFrame,
                           filename: str = 'trend_analysis.xlsx',
                           moving_average_window=12,
                           auto_correlation_lag=1) -> pd.DataFrame:
    """
    Выполняет анализ тренда, включая нахождение скользящего среднего, дифференциала, автокорреляции и экстремумов.

    :param auto_correlation_lag: Задержка для вычисления автокорреляции (по умолчанию 1).
    :param moving_average_window: Размер окна для скользящего среднего (по умолчанию 12).
    :param data: DataFrame с исходными данными.
    :param filename: Имя файла для сохранения.
    """
    result_data = data.copy()

    result_data['moving_average'] = moving_average(result_data['Python'], window=moving_average_window)
    result_data['moving_average_manual'] = moving_average_manual(result_data['Python'], window=moving_average_window)
    result_data['differential'] = differentiate(result_data['Python'])
    result_data['auto_correlation'] = auto_correlation(result_data['Python'], lag=auto_correlation_lag)

    # Поиск точек экстремума
    extremes = find_extremes(result_data['Python'])
    result_data = pd.concat([result_data, extremes], axis=1)

    # Сохранение результатов анализа в Excel
    save_to_excel(result_data, filename)

    return result_data
