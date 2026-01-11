"""
Plotting functions for the Strategy Backtester.
"""
import polars as pl
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import List, Dict, Optional

def render_price_chart_with_indicators(
    df: pl.DataFrame,
    equity_ticker: str,
    signals: List[str],
    params: Dict,
    signal_col: Optional[str] = None,
    forward_return_col: Optional[str] = None
) -> go.Figure:
    """
    Creates a multi-subplot chart with asset price and selected indicators.
    Can also display signal occurrences if signal_col and forward_return_col are provided.
    """
    if df.is_empty():
        return go.Figure()

    subplot_signals: List[str] = [s for s in signals if s in ["RSI", "VIX", "Yield Curve", "GDP"]]
    num_subplots: int = 1 + len(subplot_signals)
    
    row_heights: List[float] = [0.6] + [0.4 / len(subplot_signals)] * len(subplot_signals) if subplot_signals else [1.0]

    fig: go.Figure = make_subplots(
        rows=num_subplots,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=row_heights
    )

    # Plot 1: Equity Price and Moving Averages
    fig.add_trace(go.Scatter(x=df["date"], y=df["close"], name=equity_ticker, legendgroup="price", mode='lines'), row=1, col=1)
    
    if "Moving Average Crossover" in signals:
        ma_short: int = params.get('ma_short', 50)
        ma_long: int = params.get('ma_long', 200)
        fig.add_trace(go.Scatter(x=df["date"], y=df[f"sma_{ma_short}"], name=f"SMA({ma_short})", legendgroup="price", mode='lines'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df[f"sma_{ma_long}"], name=f"SMA({ma_long})", legendgroup="price", mode='lines'), row=1, col=1)

    # Plot signals if provided
    if signal_col and forward_return_col and signal_col in df.columns and forward_return_col in df.columns:
        signal_df = df.filter(pl.col(signal_col) == True)
        if not signal_df.is_empty():
            # Green for positive returns, Red for negative
            signal_df = signal_df.with_columns(
                pl.when(pl.col(forward_return_col) > 0)
                .then(pl.lit("green"))
                .otherwise(pl.lit("red"))
                .alias("signal_color")
            )

            fig.add_trace(
                go.Scatter(
                    x=signal_df["date"],
                    y=signal_df["close"],
                    mode='markers',
                    name='Signal',
                    marker=dict(
                        symbol='circle',
                        size=10,
                        color=signal_df["signal_color"].to_list(),
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    hovertemplate=(
                        f"<b>Date</b>: %{{x}}<br>"
                        f"<b>{equity_ticker} Close</b>: %{{y:,.2f}}<br>"
                        f"<b>Forward Return</b>: %{{customdata[0]:.2f}}%<extra></extra>"
                    ),
                    customdata=signal_df[[forward_return_col]].to_numpy(),
                    legendgroup="signals"
                ),
                row=1, col=1
            )


    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)

    # Subsequent plots for other indicators
    current_row: int = 2
    for signal in subplot_signals:
        if signal == "RSI":
            rsi_period: int = params.get('rsi_length', 14)
            fig.add_trace(go.Scatter(x=df["date"], y=df[f"rsi_{rsi_period}"], name="RSI", mode='lines'), row=current_row, col=1)
            fig.update_yaxes(title_text="RSI", row=current_row, col=1)
            # Add overbought/oversold lines
            fig.add_hline(y=params.get('rsi_overbought', 70), line_dash="dash", row=current_row, col=1, line_color="red")
            fig.add_hline(y=params.get('rsi_oversold', 30), line_dash="dash", row=current_row, col=1, line_color="green")

        elif signal == "VIX":
            fig.add_trace(go.Scatter(x=df["date"], y=df["vix"], name="VIX", mode='lines'), row=current_row, col=1)
            fig.update_yaxes(title_text="VIX", row=current_row, col=1)

        elif signal == "Yield Curve":
            fig.add_trace(go.Scatter(x=df["date"], y=df["yield_spread"], name="Yield Spread", mode='lines'), row=current_row, col=1)
            fig.update_yaxes(title_text="Spread", row=current_row, col=1)
            fig.add_hline(y=0, line_dash="dash", row=current_row, col=1, line_color="grey")

        elif signal == "GDP":
            fig.add_trace(go.Bar(x=df["date"], y=df["gdp_growth"], name="GDP Growth (QoQ %)"), row=current_row, col=1)
            fig.update_yaxes(title_text="GDP Growth %", row=current_row, col=1)

        current_row += 1

    fig.update_layout(
        height=300 * num_subplots,
        title_text=f"{equity_ticker} Price and Selected Indicators",
        hovermode="x unified",
        legend_tracegroupgap=180,
    )
    fig.update_xaxes(showticklabels=True, row=num_subplots, col=1)

    return fig

def render_equity_curve_chart(
    equity_curve_df: pl.DataFrame,
    title: str = "Strategy Equity Curve",
    height: int = 400
) -> go.Figure:
    """
    Renders the equity curve of the backtested strategy.
    """
    if equity_curve_df.is_empty():
        return go.Figure()

    fig: go.Figure = go.Figure()
    fig.add_trace(go.Scatter(x=equity_curve_df["date"], y=equity_curve_df["equity_curve"], mode='lines', name='Equity Curve'))

    fig.update_layout(
        title_text=title,
        yaxis_title="Equity Value",
        xaxis_title="Date",
        hovermode="x unified",
        template="plotly_white",
        height=height
    )
    return fig

