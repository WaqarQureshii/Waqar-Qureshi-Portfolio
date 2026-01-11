"""
Functions for calculating backtesting metrics.
"""
import polars as pl
from typing import Dict, Any

def calculate_signal_based_metrics(
    df: pl.DataFrame,
    forward_return_col: str,
    signal_col: str = "signal"
) -> Dict[str, Any]:
    """
    Calculates signal-based performance metrics.

    Args:
        df: DataFrame containing 'signal' and 'forward_return' columns.
        forward_return_col: Name of the column containing forward returns.
        signal_col: Name of the boolean column indicating signal occurrences.

    Returns:
        A dictionary of performance metrics.
    """
    # Filter to only signal occurrences with non-null forward returns
    signal_df = df.filter(
        (pl.col(signal_col) == True) &
        (pl.col(forward_return_col).is_not_null())
    )

    if len(signal_df) == 0:
        return {
            "total_signals": 0,
            "winning_signals": 0,
            "losing_signals": 0,
            "win_rate": 0.0,
            "average_return_per_signal": 0.0,
            "cumulative_return_signals": 0.0,
        }

    total_signals = len(signal_df)
    winning_signals = signal_df.filter(pl.col(forward_return_col) > 0).shape[0]
    losing_signals = total_signals - winning_signals
    win_rate = (winning_signals / total_signals) * 100 if total_signals > 0 else 0.0
    average_return_per_signal = signal_df[forward_return_col].mean()
    cumulative_return_signals = signal_df[forward_return_col].sum()

    return {
        "total_signals": total_signals,
        "winning_signals": winning_signals,
        "losing_signals": losing_signals,
        "win_rate": round(win_rate, 2),
        "average_return_per_signal": round(average_return_per_signal, 2),
        "cumulative_return_signals": round(cumulative_return_signals, 2),
    }

