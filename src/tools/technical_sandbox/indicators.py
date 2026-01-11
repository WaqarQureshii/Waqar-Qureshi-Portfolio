"""
Technical indicator calculation functions for the Technical Sandbox.
"""
import polars as pl
import talib
import numpy as np
from typing import Optional, List

def calculate_sma(
    df: pl.DataFrame,
    period: int,
    value_col: str = "close"
) -> pl.DataFrame:
    """Calculates the Simple Moving Average (SMA) using TA-Lib."""
    values: np.ndarray = df[value_col].to_numpy()
    sma: np.ndarray = talib.SMA(values, timeperiod=period)
    return df.with_columns(
        pl.Series(name=f"sma_{period}", values=sma)
    )

def calculate_ema(
    df: pl.DataFrame,
    period: int,
    value_col: str = "close"
) -> pl.DataFrame:
    """Calculates the Exponential Moving Average (EMA) using TA-Lib."""
    values: np.ndarray = df[value_col].to_numpy()
    ema: np.ndarray = talib.EMA(values, timeperiod=period)
    return df.with_columns(
        pl.Series(name=f"ema_{period}", values=ema)
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

def calculate_macd(
    df: pl.DataFrame,
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
    value_col: str = "close"
) -> pl.DataFrame:
    """Calculates the Moving Average Convergence Divergence (MACD) using TA-Lib."""
    values: np.ndarray = df[value_col].to_numpy()
    macd, macdsignal, macdhist = talib.MACD(
        values,
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod
    )
    return df.with_columns([
        pl.Series(name="macd", values=macd),
        pl.Series(name="macdsignal", values=macdsignal),
        pl.Series(name="macdhist", values=macdhist)
    ])
