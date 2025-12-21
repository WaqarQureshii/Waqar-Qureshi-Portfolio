"""
Reusable chart components and data transformation utilities.

This module provides:
- Data transformation functions for time series analysis
- Plotly chart builders for dual-axis visualizations
- Standard styling and layout configurations
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# DATA TRANSFORMATION FUNCTIONS
# =============================================================================

def resample_to_monthly(
    df: pl.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    agg_method: str = "last"
)  -> pl.DataFrame:
    """
    Resample time series data to monthly frequency.

    Args:
        df: Polars DataFrame with time series data
        date_col: Name of the date column
        value_col: Name of the value column to aggregate
        agg_method: Aggregation method ("last", "mean", "sum", "first")

    Returns:
        Monthly resampled DataFrame

    Example:
        >>> daily_df = pl.DataFrame({
        ...     "date": [...],
        ...     "value": [...]
        ... })
        >>> monthly_df = resample_to_monthly(daily_df)
    """
    # Ensure date column is datetime type
    if df[date_col].dtype != pl.Date and df[date_col].dtype != pl.Datetime:
        df = df.with_columns(pl.col(date_col).cast(pl.Date))

    # Sort by date
    df = df.sort(date_col)

    # Define aggregation expression based on method
    agg_expr = {
        "last": pl.col(value_col).last(),
        "first": pl.col(value_col).first(),
        "mean": pl.col(value_col).mean(),
        "sum": pl.col(value_col).sum()
    }

    if agg_method not in agg_expr:
        raise ValueError(f"Invalid agg_method: {agg_method}. Must be one of {list(agg_expr.keys())}")

    # Resample to monthly
    monthly_df = df.group_by_dynamic(
        date_col,
        every="1mo",
        closed="right"
    ).agg([
        agg_expr[agg_method].alias(value_col)
    ])

    return monthly_df


def resample_to_quarterly(
    df: pl.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    agg_method: str = "last"
) -> pl.DataFrame:
    """
    Resample time series data to quarterly frequency.

    Args:
        df: Polars DataFrame with time series data
        date_col: Name of the date column
        value_col: Name of the value column to aggregate
        agg_method: Aggregation method ("last", "mean", "sum", "first")

    Returns:
        Quarterly resampled DataFrame

    Example:
        >>> monthly_df = pl.DataFrame({
        ...     "date": [...],
        ...     "value": [...]
        ... })
        >>> quarterly_df = resample_to_quarterly(monthly_df)
    """
    # Ensure date column is datetime type
    if df[date_col].dtype != pl.Date and df[date_col].dtype != pl.Datetime:
        df = df.with_columns(pl.col(date_col).cast(pl.Date))

    # Sort by date
    df = df.sort(date_col)

    # Define aggregation expression based on method
    agg_expr = {
        "last": pl.col(value_col).last(),
        "first": pl.col(value_col).first(),
        "mean": pl.col(value_col).mean(),
        "sum": pl.col(value_col).sum()
    }

    if agg_method not in agg_expr:
        raise ValueError(f"Invalid agg_method: {agg_method}. Must be one of {list(agg_expr.keys())}")

    # Resample to quarterly
    quarterly_df = df.group_by_dynamic(
        date_col,
        every="1q",
        closed="right"
    ).agg([
        agg_expr[agg_method].alias(value_col)
    ])

    return quarterly_df


def calculate_percentage_of_series(
    numerator_df: pl.DataFrame,
    denominator_df: pl.DataFrame,
    date_col: str = "date",
    num_value_col: str = "value",
    denom_value_col: str = "value",
    result_col: str = "percentage"
) -> pl.DataFrame:
    """
    Calculate (numerator / denominator) * 100 for aligned time series.

    Args:
        numerator_df: DataFrame with numerator series
        denominator_df: DataFrame with denominator series
        date_col: Name of the date column
        num_value_col: Column name for numerator values
        denom_value_col: Column name for denominator values
        result_col: Name for the resulting percentage column

    Returns:
        DataFrame with date and percentage columns

    Example:
        >>> m2_pct_gdp = calculate_percentage_of_series(m2_df, gdp_df)
    """
    # Rename columns to avoid conflicts
    num_renamed = numerator_df.select([
        pl.col(date_col),
        pl.col(num_value_col).alias("_num")
    ])

    denom_renamed = denominator_df.select([
        pl.col(date_col),
        pl.col(denom_value_col).alias("_denom")
    ])

    # Inner join on date
    result = num_renamed.join(denom_renamed, on=date_col, how="inner")

    # Calculate percentage
    result = result.with_columns([
        ((pl.col("_num") / pl.col("_denom")) * 100).alias(result_col)
    ]).select([date_col, result_col])

    # Drop nulls
    result = result.drop_nulls()

    return result

def calculate_ratio(
    numerator_df: pl.DataFrame,
    denominator_df: pl.DataFrame,
    date_col: str = "date",
    num_value_col: str = "value",
    denom_value_col: str = "value",
    result_col: str = "ratio"
) -> pl.DataFrame:
    """
    Calculate numerator / denominator for aligned time series.

    Args:
        numerator_df: DataFrame with numerator series
        denominator_df: DataFrame with denominator series
        date_col: Name of the date column
        num_value_col: Column name for numerator values
        denom_value_col: Column name for denominator values
        result_col: Name for the resulting ratio column

    Returns:
        DataFrame with date and ratio columns

    Example:
        >>> hyg_tlt_ratio = calculate_ratio(hyg_df, tlt_df)
    """
    # Rename columns to avoid conflicts
    num_renamed = numerator_df.select([
        pl.col(date_col),
        pl.col(num_value_col).alias("_num")
    ])

    denom_renamed = denominator_df.select([
        pl.col(date_col),
        pl.col(denom_value_col).alias("_denom")
    ])

    # Inner join on date
    result = num_renamed.join(denom_renamed, on=date_col, how="inner")

    # Calculate ratio (handle division by zero)
    result = result.with_columns([
        pl.when(pl.col("_denom") > 0)
          .then(pl.col("_num") / pl.col("_denom"))
          .otherwise(None)
          .alias(result_col)
    ]).select([date_col, result_col])

    # Drop nulls
    result = result.drop_nulls()

    return result

def merge_multiple_series(
    series_list: List[Tuple[pl.DataFrame, str]],
    date_col: str = "date"
) -> pl.DataFrame:
    """
    Merge multiple time series DataFrames on date column.

    Args:
        series_list: List of (DataFrame, column_name) tuples
        date_col: Name of the date column

    Returns:
        Merged DataFrame with all series

    Example:
        >>> merged = merge_multiple_series([
        ...     (m2_gdp_df, "m2_pct_gdp"),
        ...     (sp500_df, "sp500")
        ... ])
    """
    if not series_list:
        raise ValueError("series_list cannot be empty")

    # Start with first series
    result = series_list[0][0].select([date_col, series_list[0][1]])

    # Join remaining series
    for df, col_name in series_list[1:]:
        series_df = df.select([date_col, col_name])
        result = result.join(series_df, on=date_col, how="inner")

    # Sort by date
    result = result.sort(date_col)

    return result


def calculate_pct_change(
    df: pl.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    result_col: str = "inflation_rate",
    noPeriods: int = 12
) -> pl.DataFrame:
    """
    Calculate percentage change over a provided period of time.

    Formula: ((Value_t / Value_t-n) - 1) * 100

    Args:
        df: DataFrame with monthly CPI data
        date_col: Name of the date column
        value_col: Name of the value column
        result_col: Name for the resulting percentage change column

    Returns:
        DataFrame with date and percentage change columns

    Example:
        >>> inflation_df = calculate_pct_change(cpi_df)
    """
    # Sort by date
    df = df.sort(date_col)

    # Calculate percentage change over indicated period
    df = df.with_columns([
        (pl.col(value_col).pct_change(n=noPeriods) * 100).alias(result_col)
    ])

    # Select relevant columns and drop nulls
    result = df.select([date_col, value_col, result_col]).drop_nulls()

    return result


@st.cache_data(show_spinner=False)
def calculate_forward_returns(
    df: pl.DataFrame,
    value_col: str,
    forward_periods: int,
    date_col: str = "date",
    result_col: str = "forward_return"
) -> pl.DataFrame:
    """
    Calculate forward N-period percentage returns.

    Formula: ((Value_t+N / Value_t) - 1) * 100

    Args:
        df: DataFrame with time series data (must be sorted by date)
        value_col: Column containing values (e.g., "sp500")
        forward_periods: Number of periods to look ahead (e.g., 7, 30, 100)
        date_col: Name of date column
        result_col: Name for resulting forward return column

    Returns:
        DataFrame with forward_return column (null for last N rows)

    Example:
        >>> sp500_with_forward = calculate_forward_returns(
        ...     sp500_df,
        ...     value_col="close",
        ...     forward_periods=30
        ... )
    """
    # Sort by date to ensure correct ordering
    df = df.sort(date_col)

    # Calculate forward returns using shift(-N)
    # shift(-N) moves values backward, effectively looking N periods ahead
    # Handle division by zero with null check
    df = df.with_columns([
        pl.when(pl.col(value_col) > 0)
          .then((pl.col(value_col).shift(-forward_periods) / pl.col(value_col) - 1) * 100)
          .otherwise(None)
          .alias(result_col)
    ])

    return df


@st.cache_data(show_spinner=False)
def detect_signal_occurrences(
    df: pl.DataFrame,
    ratio_col: str,
    ratio_pct_col: str,
    overlay_col: str,
    overlay_pct_col: str,
    ratio_direction: str,  # "increase" or "decrease"
    ratio_threshold: float,  # percentage
    overlay_direction: str,  # "increase" or "decrease"
    overlay_threshold: float,  # percentage
    date_col: str = "date"
) -> pl.DataFrame:
    """
    Identify dates where both ratio and overlay conditions are met.

    Args:
        df: DataFrame with time series data
        ratio_col: Column name for ratio values
        ratio_pct_col: Column name for ratio percentage change
        overlay_col: Column name for overlay values
        overlay_pct_col: Column name for overlay percentage change
        ratio_direction: "increase" or "decrease" for ratio condition
        ratio_threshold: Minimum percentage change required (absolute value)
        overlay_direction: "increase" or "decrease" for overlay condition
        overlay_threshold: Minimum percentage change required (absolute value)
        date_col: Name of date column

    Returns:
        DataFrame with additional 'signal' boolean column

    Example:
        >>> signals_df = detect_signal_occurrences(
        ...     df=merged_df,
        ...     ratio_col="hyg_tlt_ratio",
        ...     ratio_pct_col="ratio_pct_change",
        ...     overlay_col="sp500",
        ...     overlay_pct_col="sp500_pct_change",
        ...     ratio_direction="increase",
        ...     ratio_threshold=2.0,
        ...     overlay_direction="decrease",
        ...     overlay_threshold=2.0
        ... )
    """
    # Create condition expressions based on direction
    ratio_condition = (
        (pl.col(ratio_pct_col) >= ratio_threshold)
        if ratio_direction == "increase"
        else (pl.col(ratio_pct_col) <= -ratio_threshold)
    )

    overlay_condition = (
        (pl.col(overlay_pct_col) >= overlay_threshold)
        if overlay_direction == "increase"
        else (pl.col(overlay_pct_col) <= -overlay_threshold)
    )

    # Add signal column (both conditions must be true)
    result = df.with_columns([
        (ratio_condition & overlay_condition).alias("signal")
    ])

    return result


def calculate_signal_metrics(
    df: pl.DataFrame,
    signal_col: str = "signal",
    forward_return_col: str = "forward_return"
) -> Dict[str, Any]:
    """
    Calculate aggregate metrics for signal occurrences.

    Args:
        df: DataFrame with signal and forward return columns
        signal_col: Name of boolean signal column
        forward_return_col: Name of forward return column

    Returns:
        Dictionary with keys: count, avg_return, min_return, max_return, win_rate

    Example:
        >>> metrics = calculate_signal_metrics(
        ...     df=signals_df,
        ...     signal_col="signal",
        ...     forward_return_col="sp500_forward_30d"
        ... )
        >>> print(f"Found {metrics['count']} signals with {metrics['win_rate']:.1f}% win rate")
    """
    # Filter to only signal occurrences with non-null forward returns
    signal_df = df.filter(
        (pl.col(signal_col) == True) &
        (pl.col(forward_return_col).is_not_null())
    )

    if len(signal_df) == 0:
        return {
            "count": 0,
            "avg_return": None,
            "min_return": None,
            "max_return": None,
            "win_rate": None
        }

    # Calculate win rate (percentage of signals with positive returns)
    positive_signals = signal_df.filter(pl.col(forward_return_col) > 0)
    win_rate = (len(positive_signals) / len(signal_df)) * 100

    return {
        "count": len(signal_df),
        "avg_return": signal_df[forward_return_col].mean(),
        "min_return": signal_df[forward_return_col].min(),
        "max_return": signal_df[forward_return_col].max(),
        "win_rate": win_rate
    }


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def apply_standard_layout(
    fig: go.Figure,
    title: str = "",
    height: int = 500,
    show_legend: bool = True
) -> go.Figure:
    """
    Apply consistent styling to Plotly charts.

    Args:
        fig: Plotly figure object
        title: Chart title
        height: Chart height in pixels
        show_legend: Whether to show legend

    Returns:
        Styled figure
    """
    fig.update_layout(
        title=title,
        height=height,
        hovermode="x unified",
        template="plotly_white",
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=80, r=80, t=80, b=60)
    )

    return fig


def create_dual_axis_chart(
    df: pl.DataFrame,
    date_col: str,
    left_y_col: str,
    right_y_col: str,
    left_trace_type: str = "line",
    right_trace_type: str = "line",
    left_y_title: str = "",
    right_y_title: str = "",
    left_trace_name: str = "",
    right_trace_name: str = "",
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Create a dual-axis chart with two time series.

    Args:
        df: Polars DataFrame with aligned data
        date_col: Name of the date column
        left_y_col: Column for left y-axis
        right_y_col: Column for right y-axis
        left_trace_type: Type of trace for left axis ("line", "bar")
        right_trace_type: Type of trace for right axis ("line", "bar")
        left_y_title: Title for left y-axis
        right_y_title: Title for right y-axis
        left_trace_name: Name for left trace (legend)
        right_trace_name: Name for right trace (legend)
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly figure with dual axes

    Example:
        >>> fig = create_dual_axis_chart(
        ...     df=merged_df,
        ...     date_col="date",
        ...     left_y_col="tbill_rate",
        ...     right_y_col="inflation",
        ...     left_y_title="T-Bill Rate (%)",
        ...     right_y_title="Inflation (%)"
        ... )
    """
    # Convert to pandas for Plotly compatibility
    pdf = df.to_pandas()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add left trace
    if left_trace_type == "line":
        fig.add_trace(
            go.Scatter(
                x=pdf[date_col],
                y=pdf[left_y_col],
                name=left_trace_name or left_y_col,
                line=dict(color="#1f77b4", width=2)
            ),
            secondary_y=False
        )
    elif left_trace_type == "bar":
        fig.add_trace(
            go.Bar(
                x=pdf[date_col],
                y=pdf[left_y_col],
                name=left_trace_name or left_y_col,
                marker=dict(color="#1f77b4")
            ),
            secondary_y=False
        )

    # Add right trace
    if right_trace_type == "line":
        fig.add_trace(
            go.Scatter(
                x=pdf[date_col],
                y=pdf[right_y_col],
                name=right_trace_name or right_y_col,
                line=dict(color="#ff7f0e", width=2)
            ),
            secondary_y=True
        )
    elif right_trace_type == "bar":
        fig.add_trace(
            go.Bar(
                x=pdf[date_col],
                y=pdf[right_y_col],
                name=right_trace_name or right_y_col,
                marker=dict(color="#ff7f0e")
            ),
            secondary_y=True
        )

    # Set axis titles
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=left_y_title, secondary_y=False)
    fig.update_yaxes(title_text=right_y_title, secondary_y=True)

    # Apply standard layout
    fig = apply_standard_layout(fig, title=title, height=height)

    return fig


def create_bar_line_chart(
    df: pl.DataFrame,
    date_col: str,
    bar_col: str,
    line_col: str,
    bar_name: str = "",
    line_name: str = "",
    bar_y_title: str = "",
    line_y_title: str = "",
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Create a chart with bars on left axis and line on right axis.

    Args:
        df: Polars DataFrame with aligned data
        date_col: Name of the date column
        bar_col: Column for bar chart (left axis)
        line_col: Column for line chart (right axis)
        bar_name: Name for bar trace (legend)
        line_name: Name for line trace (legend)
        bar_y_title: Title for left y-axis (bars)
        line_y_title: Title for right y-axis (line)
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly figure

    Example:
        >>> fig = create_bar_line_chart(
        ...     df=merged_df,
        ...     date_col="date",
        ...     bar_col="m2_pct_gdp",
        ...     line_col="sp500",
        ...     title="M2/GDP vs S&P 500"
        ... )
    """
    return create_dual_axis_chart(
        df=df,
        date_col=date_col,
        left_y_col=bar_col,
        right_y_col=line_col,
        left_trace_type="bar",
        right_trace_type="line",
        left_y_title=bar_y_title,
        right_y_title=line_y_title,
        left_trace_name=bar_name or bar_col,
        right_trace_name=line_name or line_col,
        title=title,
        height=height
    )


def create_ratio_overlay_chart(
    df: pl.DataFrame,
    date_col: str,
    ratio_col: str,
    overlay_col: str,
    ratio_name: str = "",
    overlay_name: str = "",
    ratio_y_title: str = "Ratio",
    overlay_y_title: str = "",
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Create a dual-axis line chart for ratio analysis with overlay.

    Args:
        df: Polars DataFrame with aligned data
        date_col: Name of the date column
        ratio_col: Column for ratio (left axis)
        overlay_col: Column for overlay series (right axis)
        ratio_name: Name for ratio trace (legend)
        overlay_name: Name for overlay trace (legend)
        ratio_y_title: Title for left y-axis (ratio)
        overlay_y_title: Title for right y-axis (overlay)
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly figure

    Example:
        >>> fig = create_ratio_overlay_chart(
        ...     df=merged_df,
        ...     date_col="date",
        ...     ratio_col="hyg_tlt_ratio",
        ...     overlay_col="sp500",
        ...     title="HYG/TLT Ratio vs S&P 500"
        ... )
    """
    return create_dual_axis_chart(
        df=df,
        date_col=date_col,
        left_y_col=ratio_col,
        right_y_col=overlay_col,
        left_trace_type="line",
        right_trace_type="line",
        left_y_title=ratio_y_title,
        right_y_title=overlay_y_title,
        left_trace_name=ratio_name or ratio_col,
        right_trace_name=overlay_name or overlay_col,
        title=title,
        height=height
    )


def create_ratio_overlay_chart_with_signals(
    df: pl.DataFrame,
    date_col: str,
    ratio_col: str,
    overlay_col: str,
    signal_col: str = "signal",
    ratio_pct_col: str = "ratio_pct_change",
    overlay_pct_col: str = "sp500_pct_change",
    forward_return_col: str = "forward_return",
    ratio_name: str = "",
    overlay_name: str = "",
    ratio_y_title: str = "Ratio",
    overlay_y_title: str = "",
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Create dual-axis chart with scatter markers on signal occurrences.

    Extends create_ratio_overlay_chart by adding scatter markers
    on the overlay line where signal_col == True.

    Args:
        df: Polars DataFrame with aligned data
        date_col: Name of the date column
        ratio_col: Column for ratio (left axis)
        overlay_col: Column for overlay series (right axis)
        signal_col: Boolean column indicating signal occurrences
        ratio_pct_col: Column with ratio percentage changes (for hover)
        overlay_pct_col: Column with overlay percentage changes (for hover)
        forward_return_col: Column with forward returns (for hover)
        ratio_name: Name for ratio trace (legend)
        overlay_name: Name for overlay trace (legend)
        ratio_y_title: Title for left y-axis (ratio)
        overlay_y_title: Title for right y-axis (overlay)
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly figure with dual axes and signal markers

    Example:
        >>> fig = create_ratio_overlay_chart_with_signals(
        ...     df=signals_df,
        ...     date_col="date",
        ...     ratio_col="hyg_tlt_ratio",
        ...     overlay_col="sp500",
        ...     signal_col="signal",
        ...     title="Risk Signals: HYG/TLT vs S&P 500"
        ... )
    """
    # Convert to pandas for Plotly compatibility
    pdf = df.to_pandas()

    # Create base dual-axis figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add ratio line (left axis)
    fig.add_trace(
        go.Scatter(
            x=pdf[date_col],
            y=pdf[ratio_col],
            name=ratio_name or ratio_col,
            line=dict(color="#1f77b4", width=2),
            mode="lines"
        ),
        secondary_y=False
    )

    # Add overlay line (right axis) - S&P 500
    fig.add_trace(
        go.Scatter(
            x=pdf[date_col],
            y=pdf[overlay_col],
            name=overlay_name or overlay_col,
            line=dict(color="#ff7f0e", width=2),
            mode="lines"
        ),
        secondary_y=True
    )

    # Add scatter markers for signal occurrences
    # Filter to only dates where signal == True
    signal_pdf = pdf[pdf[signal_col] == True].copy()

    if len(signal_pdf) > 0:
        # Prepare customdata for hover template
        # Include ratio_pct_change, overlay_pct_change, and forward_return
        customdata = signal_pdf[[ratio_pct_col, overlay_pct_col, forward_return_col]].values

        fig.add_trace(
            go.Scatter(
                x=signal_pdf[date_col],
                y=signal_pdf[overlay_col],  # Plot on S&P 500 values
                name="Signal Occurrence",
                mode="markers",
                marker=dict(
                    color="red",
                    size=10,
                    symbol="circle",
                    line=dict(color="darkred", width=1)
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b>Signal Date</b>: %{x}<br>" +
                    f"<b>{overlay_name or overlay_col}</b>: %{{y:,.2f}}<br>" +
                    f"<b>{ratio_name or ratio_col} Change</b>: %{{customdata[0]:+.2f}}%<br>" +
                    f"<b>{overlay_name or overlay_col} Change</b>: %{{customdata[1]:+.2f}}%<br>" +
                    "<b>Forward Return</b>: %{customdata[2]:+.2f}%<br>" +
                    "<extra></extra>"
                )
            ),
            secondary_y=True
        )

    # Set axis titles
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=ratio_y_title, secondary_y=False)
    fig.update_yaxes(title_text=overlay_y_title, secondary_y=True)

    # Apply standard layout
    fig = apply_standard_layout(fig, title=title, height=height)

    return fig


def create_dual_subplot_chart(
    df: pl.DataFrame,
    date_col: str,
    # Top subplot params
    top_chart_title: str,
    top_left_col: str,
    top_right_col: str,
    top_left_name: str,
    top_right_name: str,
    top_left_title: str,
    top_right_title: str,
    # Bottom subplot params
    bottom_chart_title: str,
    bottom_left_col: str,
    bottom_right_col: str,
    bottom_left_name: str,
    bottom_right_name: str,
    bottom_left_title: str,
    bottom_right_title: str,
    bottom_left_type: str = "line",
    bottom_right_type: str = "line",
    # General params
    title: str = "",
    height: int = 900
) -> go.Figure:
    """
    Create a 2-row subplot chart with dual y-axes for each row.

    Args:
        df: Polars DataFrame with aligned data
        date_col: Name of the date column
        top_chart_title: Title for the top subplot
        top_left_col: Column for top subplot left y-axis
        top_right_col: Column for top subplot right y-axis
        top_left_name: Name for top left trace (legend)
        top_right_name: Name for top right trace (legend)
        top_left_title: Title for top subplot left y-axis
        top_right_title: Title for top subplot right y-axis
        bottom_chart_title: Title for the bottom subplot
        bottom_left_col: Column for bottom subplot left y-axis
        bottom_right_col: Column for bottom subplot right y-axis
        bottom_left_name: Name for bottom left trace (legend)
        bottom_right_name: Name for bottom right trace (legend)
        bottom_left_title: Title for bottom subplot left y-axis
        bottom_right_title: Title for bottom subplot right y-axis
        bottom_left_type: Type of trace for bottom left ("line" or "bar")
        bottom_right_type: Type of trace for bottom right ("line" or "bar")
        title: Overall chart title
        height: Total chart height in pixels

    Returns:
        Plotly figure with 2-row subplots

    Example:
        >>> fig = create_dual_subplot_chart(
        ...     df=merged_df,
        ...     date_col="date",
        ...     top_left_col="tbill_rate",
        ...     top_right_col="inflation_rate",
        ...     top_left_name="T-Bill Rate",
        ...     top_right_name="Inflation",
        ...     top_left_title="T-Bill Rate (%)",
        ...     top_right_title="Inflation (%)",
        ...     bottom_left_col="real_rate",
        ...     bottom_right_col="m2_supply",
        ...     bottom_left_name="Real Rate",
        ...     bottom_right_name="M2 Supply",
        ...     bottom_left_title="Real Rate (%)",
        ...     bottom_right_title="M2 (Billions)",
        ...     bottom_right_type="bar"
        ... )
    """
    # Create 2-row subplot with secondary y-axes for both rows
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[
            [{"secondary_y": True}],  # Top row with secondary y-axis
            [{"secondary_y": True}]   # Bottom row with secondary y-axis
        ],
        shared_xaxes=True,  # Share x-axis between subplots
        vertical_spacing=0.12,  # Space between subplots
        subplot_titles=(
            "Risk-Free Rates vs Inflation",
            "Real Rate vs Money Supply"
        )
    )

    # Top subplot - Add left trace (T-Bill)
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[top_left_col],
            name=top_left_name,
            line=dict(color="#1f77b4", width=2)
        ),
        row=1, col=1, secondary_y=False
    )

    # Top subplot - Add right trace (Inflation)
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[top_right_col],
            name=top_right_name,
            line=dict(color="#ff7f0e", width=2)
        ),
        row=1, col=1, secondary_y=True
    )

    # Bottom subplot - Add left trace (Real Rate)
    if bottom_left_type == "line":
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[bottom_left_col],
                name=bottom_left_name,
                line=dict(color="#5fa359", width=2)
            ),
            row=2, col=1, secondary_y=False
        )
    elif bottom_left_type == "bar":
        fig.add_trace(
            go.Bar(
                x=df[date_col],
                y=df[bottom_left_col],
                name=bottom_left_name,
                marker=dict(color="#5fa359")
            ),
            row=2, col=1, secondary_y=False
        )

    # Bottom subplot - Add right trace (M2 Supply)
    if bottom_right_type == "line":
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[bottom_right_col],
                name=bottom_right_name,
                line=dict(color="#d62728", width=2)
            ),
            row=2, col=1, secondary_y=True
        )
    elif bottom_right_type == "bar":
        fig.add_trace(
            go.Bar(
                x=df[date_col],
                y=df[bottom_right_col],
                name=bottom_right_name,
                marker=dict(color="#d62728")
            ),
            row=2, col=1, secondary_y=True
        )

    # Update y-axes for both subplots
    fig.update_yaxes(title_text=top_left_title, row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text=top_right_title, row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text=bottom_left_title, row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text=bottom_right_title, row=2, col=1, secondary_y=True)

    # Update x-axis (only bottom row needs label due to shared_xaxes)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    # Apply standard layout
    fig.update_layout(
        title=title,
        height=height,
        hovermode="x unified",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=80, r=80, t=120, b=60)
    )

    return fig
