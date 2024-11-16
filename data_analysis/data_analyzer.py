import pandas as pd

from .models import DataPoint


def moving_average(data_points: list[DataPoint], window_size: int) -> pd.Series:
    df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in data_points])
    df.set_index('timestamp', inplace=True)
    ma = df['value'].rolling(window=window_size).mean()
    return ma


def calculate_difference(data_points: list[DataPoint]) -> pd.Series:
    df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in data_points])
    df.set_index('timestamp', inplace=True)
    diff = df['value'].diff()
    return diff


def autocorrelation(data_points: list[DataPoint], lag: int) -> float:
    df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in data_points])
    df.set_index('timestamp', inplace=True)
    return df['value'].autocorr(lag=lag)


def find_extrema(data_points: list[DataPoint]) -> pd.DataFrame:
    df = pd.DataFrame([{'timestamp': dp.timestamp, 'value': dp.value} for dp in data_points])
    df.set_index('timestamp', inplace=True)
    df['min'] = df['value'][(df['value'].shift(1) > df['value']) & (df['value'].shift(-1) > df['value'])]
    df['max'] = df['value'][(df['value'].shift(1) < df['value']) & (df['value'].shift(-1) < df['value'])]
    return df[['min', 'max']]


def save_to_excel(data_frames: list[pd.DataFrame], operations: list[str], source: str):
    with pd.ExcelWriter(f"results_{source}_{operations[-1]}.xlsx") as writer:
        for i, df in enumerate(data_frames):
            df.to_excel(writer, sheet_name=operations[i])
