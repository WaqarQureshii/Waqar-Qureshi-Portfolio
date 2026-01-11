"""
Technical indicator calculation functions.
"""
import polars as pl
import talib
import numpy as np
from typing import Union, List

def calculate_moving_average(
    df: pl.DataFrame,
    period: int,
    value_col: str = "close"
) -> pl.DataFrame:
    """Calculates the simple moving average using TA-Lib."""
    values: np.ndarray = df[value_col].to_numpy()
    sma: np.ndarray = talib.SMA(values, timeperiod=period)
    return df.with_columns(
        pl.Series(name=f"sma_{period}", values=sma)
    )

def calculate_rsi(
    df: pl.DataFrame,
    period: int = 14,
    value_col: str = "close"
) -> pl.DataFrame:
    """Calculates the Relative Strength Index (RSI) using TA-Lib."""
    values: np.ndarray = df[value_col].to_numpy()
    rsi: np.ndarray = talib.RSI(values, timeperiod=period)
    return df.with_columns(
        pl.Series(name=f"rsi_{period}", values=rsi)
    )
