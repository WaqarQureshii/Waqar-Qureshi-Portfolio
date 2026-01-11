"""
Core backtesting engine for the Strategy Backtester.
"""
import polars as pl
from typing import List, Dict

from src.components.charts import calculate_forward_returns # Reusing existing function

def run_backtest(
    df: pl.DataFrame,
    signals: List[str],
    params: Dict,
    forward_return_period: int
) -> pl.DataFrame:
    """
    Identifies signal occurrences and calculates forward returns based on selected strategies.
    """
    # Initialize signal column
    df = df.with_columns(pl.lit(False).alias("signal"))

    # --- Implement Signal Logic ---
    # Each signal will generate a boolean series, which will then be combined.
    signal_conditions = []

    if "RSI" in signals and 'rsi_length' in params and 'rsi_oversold' in params and 'rsi_overbought' in params:
        rsi_period = params['rsi_length']
        rsi_oversold = params['rsi_oversold']
        rsi_overbought = params['rsi_overbought']

        # Example: Buy signal when RSI crosses above oversold from below
        # For simplicity, let's just say signal if RSI is below oversold or above overbought
        # We can refine this later to be more sophisticated (e.g., crossovers)
        if f"rsi_{rsi_period}" in df.columns:
            rsi_buy_condition = pl.col(f"rsi_{rsi_period}") < rsi_oversold
            rsi_sell_condition = pl.col(f"rsi_{rsi_period}") > rsi_overbought
            signal_conditions.append(rsi_buy_condition | rsi_sell_condition)


    if "Moving Average Crossover" in signals and 'ma_short' in params and 'ma_long' in params:
        ma_short = params['ma_short']
        ma_long = params['ma_long']

        if f"sma_{ma_short}" in df.columns and f"sma_{ma_long}" in df.columns:
            # Golden Cross: Short MA crosses above Long MA (buy signal)
            golden_cross = (
                (pl.col(f"sma_{ma_short}") > pl.col(f"sma_{ma_long}")) &
                (pl.col(f"sma_{ma_short}").shift(1) <= pl.col(f"sma_{ma_long}").shift(1))
            )
            # Death Cross: Short MA crosses below Long MA (sell signal)
            death_cross = (
                (pl.col(f"sma_{ma_short}") < pl.col(f"sma_{ma_long}")) &
                (pl.col(f"sma_{ma_short}").shift(1) >= pl.col(f"sma_{ma_long}").shift(1))
            )
            signal_conditions.append(golden_cross | death_cross)

    if "VIX" in signals and 'vix_threshold' in params:
        vix_threshold = params['vix_threshold']
        if "vix" in df.columns:
            # Signal when VIX is above threshold (high fear)
            vix_condition = pl.col("vix") > vix_threshold
            signal_conditions.append(vix_condition)

    if "Yield Curve" in signals: # and 'yield_curve_short' in params and 'yield_curve_long' in params:
        if "yield_spread" in df.columns:
            # Signal when yield curve is inverted (negative spread)
            yield_curve_condition = pl.col("yield_spread") < 0
            signal_conditions.append(yield_curve_condition)

    if "GDP" in signals:
        if "gdp_growth" in df.columns:
            # Signal when GDP growth is negative (recessionary signal)
            gdp_condition = pl.col("gdp_growth") < 0
            signal_conditions.append(gdp_condition)

    # Combine all signal conditions. For now, let's use an OR logic.
    # A signal is triggered if ANY of the selected indicators trigger.
    # This can be made more sophisticated later (e.g., AND logic, custom combinations).
    if signal_conditions:
        combined_signal = signal_conditions[0]
        for i in range(1, len(signal_conditions)):
            combined_signal = combined_signal | signal_conditions[i]
        df = df.with_columns(combined_signal.alias("signal"))
    
    # Calculate forward returns for the equity based on the 'close' price
    # Only calculate forward returns if there are actual signals
    if df["signal"].sum() > 0:
        df = calculate_forward_returns(
            df=df,
            value_col="close",
            forward_periods=forward_return_period,
            date_col="date",
            result_col=f"forward_return_{forward_return_period}d"
        )
    else:
        # If no signals, fill forward return column with nulls
        df = df.with_columns(pl.lit(None, dtype=pl.Float64).alias(f"forward_return_{forward_return_period}d"))

    return df


def calculate_equity_curve(
    df: pl.DataFrame,
    forward_return_col: str,
    signal_col: str = "signal",
    initial_capital: float = 1000.0
) -> pl.DataFrame:
    """
    Calculates the equity curve based on signal-triggered forward returns.

    Args:
        df: DataFrame containing 'signal', 'date', and 'forward_return' columns.
        forward_return_col: Name of the column containing forward returns.
        signal_col: Name of the boolean column indicating signal occurrences.
        initial_capital: Starting capital for the equity curve.

    Returns:
        DataFrame with 'date' and 'equity_curve' columns.
    """
    # Filter for signal dates and corresponding forward returns
    signal_returns = df.filter(pl.col(signal_col)).select([
        "date",
        pl.col(forward_return_col).alias("returns_pct")
    ]).drop_nulls()

    if signal_returns.is_empty():
        # If no signals, return a flat equity curve
        # Ensure a date range if df is not empty to avoid Plotly errors with empty data
        if not df.is_empty():
            min_date = df["date"].min()
            max_date = df["date"].max()
            date_range = pl.date_range(start=min_date, end=max_date, interval="1d")
            return pl.DataFrame({
                "date": date_range,
                "equity_curve": [initial_capital] * len(date_range)
            })
        else:
            return pl.DataFrame({"date": [], "equity_curve": []}, schema={"date": pl.Date, "equity_curve": pl.Float64})


    # Convert percentage returns to decimal returns
    signal_returns = signal_returns.with_columns(
        (pl.col("returns_pct") / 100).alias("returns_decimal")
    )

    # Sort by date
    signal_returns = signal_returns.sort("date")

    # Calculate cumulative product of (1 + returns)
    # Start with initial capital
    equity_values = []
    current_equity = initial_capital
    
    # This approach assumes that returns are applied *at* the signal date
    # or shortly after. The exact timing can be refined based on strategy.
    for row in signal_returns.iter_rows(named=True):
        current_equity *= (1 + row["returns_decimal"])
        equity_values.append({"date": row["date"], "equity_curve": current_equity})

    equity_curve_df = pl.DataFrame(equity_values)

    # Merge with the original DataFrame dates to get a continuous curve
    # Fill missing equity values with the last known value
    all_dates = df.select("date").unique().sort("date")
    equity_curve_df = all_dates.join(equity_curve_df, on="date", how="left")
    
    # Forward fill the equity curve, starting with initial capital before first signal
    equity_curve_df = equity_curve_df.with_columns(
        pl.col("equity_curve").fill_null(strategy="forward")
    )
    # Fill any remaining NaNs (before the first signal) with initial capital
    equity_curve_df = equity_curve_df.with_columns(
        pl.col("equity_curve").fill_null(initial_capital)
    )

    return equity_curve_df
