"""
Data fetching and preparation for the Strategy Backtester.
"""
import streamlit as st
import polars as pl
from datetime import date
from typing import List, Dict

from src.data.cache_manager import CacheManager
from src.services.fred_api import FredService
from src.services.yfinance_service import YFinanceService
from src.tools.strategy_backtester.calculations import calculate_rsi, calculate_moving_average
from src.config.constants import FRED_SERIES

def get_chart_data(
    cache: CacheManager,
    fred: FredService,
    yf: YFinanceService,
    equity_ticker: str,
    signals: List[str],
    params: Dict,
    start_date: date,
    end_date: date
) -> pl.DataFrame:
    """
    Fetches and prepares all data needed for the backtester chart.
    """
    # 1. Fetch equity data
    equity_df: pl.DataFrame = cache.get_or_fetch(
        source="yfinance",
        source_id=equity_ticker,
        fetch_fn=lambda: yf.get_ticker_history(equity_ticker, start=start_date, end=end_date),
        frequency="daily",
        metadata_fn=lambda: {"ticker": equity_ticker, "name": equity_ticker},
        force_refresh=False
    )
    if equity_df.is_empty():
        return pl.DataFrame()

    # Create a base dataframe with all dates in the range
    all_dates: pl.Series = pl.date_range(start=start_date, end=end_date, interval="1d", eager=True).alias("date")
    base_df: pl.DataFrame = pl.DataFrame(all_dates)

    # Join equity data
    merged_df: pl.DataFrame = base_df.join(equity_df.select(["date", "close"]), on="date", how="left").sort("date")
    merged_df = merged_df.with_columns(pl.col("close").forward_fill())


    # 2. Fetch or calculate indicator data
    if "RSI" in signals and 'rsi_length' in params:
        merged_df = calculate_rsi(merged_df, period=params['rsi_length'])
    
    if "Moving Average Crossover" in signals and 'ma_short' in params and 'ma_long' in params:
        merged_df = calculate_moving_average(merged_df, period=params['ma_short'])
        merged_df = calculate_moving_average(merged_df, period=params['ma_long'])

    if "VIX" in signals:
        vix_df: pl.DataFrame = cache.get_or_fetch(
            source="yfinance",
            source_id="^VIX",
            fetch_fn=lambda: yf.get_ticker_history("^VIX", start=start_date, end=end_date),
            frequency="daily",
            metadata_fn=lambda: {"ticker": "^VIX", "name": "VIX"},
            force_refresh=False
        )
        if not vix_df.is_empty():
            merged_df = merged_df.join(vix_df.select(["date", "close"]).rename({"close": "vix"}), on="date", how="left")
            merged_df = merged_df.with_columns(pl.col("vix").forward_fill())

    if "Yield Curve" in signals and 'yield_curve_short' in params and 'yield_curve_long' in params:
        short_id: str = params['yield_curve_short']
        long_id: str = params['yield_curve_long']
        
        short_df: pl.DataFrame = cache.get_or_fetch(
            source="fred",
            source_id=short_id,
            fetch_fn=lambda: fred.get_series(short_id, start_date=start_date, end_date=end_date),
            frequency="daily",
            metadata_fn=lambda: fred.get_series_metadata(short_id)
        )
        long_df: pl.DataFrame = cache.get_or_fetch(
            source="fred",
            source_id=long_id,
            fetch_fn=lambda: fred.get_series(long_id, start_date=start_date, end_date=end_date),
            frequency="daily",
            metadata_fn=lambda: fred.get_series_metadata(long_id)
        )
        
        if not short_df.is_empty() and not long_df.is_empty():
            spread_df: pl.DataFrame = short_df.join(long_df, on="date", how="inner", suffix="_long")
            spread_df = spread_df.with_columns((pl.col("value_long") - pl.col("value")).alias("yield_spread"))
            merged_df = merged_df.join(spread_df.select(["date", "yield_spread"]), on="date", how="left")
            merged_df = merged_df.with_columns(pl.col("yield_spread").forward_fill())

    if "GDP" in signals:
        gdp_df: pl.DataFrame = cache.get_or_fetch(
            source="fred",
            source_id="GDPC1", # Using Real GDP
            fetch_fn=lambda: fred.get_series("GDPC1", start_date=start_date, end_date=end_date),
            frequency="quarterly",
            metadata_fn=lambda: fred.get_series_metadata("GDPC1")
        )
        if not gdp_df.is_empty():
            gdp_df = gdp_df.with_columns(
                (pl.col("value").pct_change(n=1) * 100).alias("gdp_growth")
            )
            merged_df = merged_df.join(gdp_df.select(["date", "gdp_growth"]), on="date", how="left")
            merged_df = merged_df.with_columns(pl.col("gdp_growth").forward_fill())
    
    return merged_df.drop_nulls()
