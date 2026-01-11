"""
Equity Value Playroom
Interactive tools for equity analysis and strategy testing
"""
import streamlit as st
import polars as pl
from datetime import datetime, date

from src.tools.strategy_backtester.ui import render_backtester_inputs
from src.tools.strategy_backtester.data import get_chart_data
from src.tools.strategy_backtester.plots import render_price_chart_with_indicators, render_equity_curve_chart
from src.tools.strategy_backtester.engine import run_backtest, calculate_equity_curve # Import the engine and equity curve calculator
from src.tools.strategy_backtester.metrics import calculate_signal_based_metrics # Import metrics
from src.tools.technical_sandbox.ui import render_technical_sandbox_ui # New import
from src.data.cache_manager import CacheManager
from src.services.fred_api import FredService
from src.services.yfinance_service import YFinanceService
from src.components.sidebar import render_date_range_selector, render_preset_date_ranges

st.set_page_config(
    page_title="Equity Playroom | Portfolio",
    page_icon="🎮",
    layout="wide"
)

# Initialize services
@st.cache_resource
def get_cache_manager():
    return CacheManager()

@st.cache_resource
def get_fred_service():
    return FredService()

@st.cache_resource
def get_yfinance_service():
    return YFinanceService()

cache = get_cache_manager()
fred = get_fred_service()
yf_service = get_yfinance_service()


st.title("🎮 Equity Playroom") # Changed title to be more general

# Sidebar for date controls
with st.sidebar:
    st.header("Chart Controls")
    start_date, end_date = render_date_range_selector(
        key_prefix="equity_playroom",
        default_years_back=5
    )
    preset = render_preset_date_ranges("equity_playroom")
    if preset:
        start_date, end_date = preset
        st.rerun()

strategy_tab, sandbox_tab = st.tabs(["📈 Strategy Backtester", "🔬 Technical Sandbox"])

with strategy_tab:
    st.info("This tool allows you to build and backtest custom trading strategies based on a variety of technical and economic indicators.")

    # Render inputs
    inputs = render_backtester_inputs()

    chart_df_ready = pl.DataFrame()

    # Fetch and display chart
    if inputs["equity"]:
        with st.spinner("Loading chart data..."):
            chart_df_ready = get_chart_data(
                cache=cache,
                fred=fred,
                yf=yf_service,
                equity_ticker=inputs["equity"],
                signals=inputs["signals"],
                params=inputs["parameters"],
                start_date=start_date,
                end_date=end_date
            )

        if not chart_df_ready.is_empty():
            # Render initial chart without signals
            fig = render_price_chart_with_indicators(
                df=chart_df_ready,
                equity_ticker=inputs["equity"],
                signals=inputs["signals"],
                params=inputs["parameters"],
                signal_col=None, # Pass None for signal parameters
                forward_return_col=None # Pass None for signal parameters
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Could not load data for '{inputs['equity']}'. Please check the ticker and date range.")

    # Run Backtest logic
    if inputs["run_backtest"]:
        if not chart_df_ready.is_empty():
            st.subheader("Backtest Results")
            with st.spinner("Running backtest engine..."):
                backtested_df = run_backtest(
                    df=chart_df_ready,
                    signals=inputs["signals"],
                    params=inputs["parameters"],
                    forward_return_period=inputs["forward_return_period"]
                )
            st.success("Backtest completed!")
            
            # Calculate and display metrics
            metrics = calculate_signal_based_metrics(
                df=backtested_df,
                forward_return_col=f"forward_return_{inputs['forward_return_period']}d",
                signal_col="signal"
            )

            st.subheader("Performance Metrics (Signal-Based)")
            if metrics["total_signals"] > 0:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1: st.metric("Total Signals", metrics["total_signals"])
                with col2: st.metric("Winning Signals", metrics["winning_signals"])
                with col3: st.metric("Win Rate", f"{metrics['win_rate']:.2f}%")
                with col4: st.metric("Avg Return/Signal", f"{metrics['average_return_per_signal']:.2f}%")
                with col5: st.metric("Cumulative Signal Return", f"{metrics['cumulative_return_signals']:.2f}%")
            else:
                st.info("No signals generated for the selected strategy and period.")

            # Display chart with signals after backtest
            if not backtested_df.is_empty():
                st.subheader("Signal Chart")
                fig_signals = render_price_chart_with_indicators(
                    df=backtested_df,
                    equity_ticker=inputs["equity"],
                    signals=inputs["signals"],
                    params=inputs["parameters"],
                    signal_col="signal", # New parameter
                    forward_return_col=f"forward_return_{inputs['forward_return_period']}d" # New parameter
                )
                st.plotly_chart(fig_signals, use_container_width=True)


            # Calculate and display Equity Curve
            st.subheader("Equity Curve")
            equity_curve_df = calculate_equity_curve(
                df=backtested_df,
                forward_return_col=f"forward_return_{inputs['forward_return_period']}d",
                signal_col="signal"
            )
            if not equity_curve_df.is_empty():
                fig_equity = render_equity_curve_chart(equity_curve_df)
                st.plotly_chart(fig_equity, use_container_width=True)
            else:
                st.info("No equity curve to display as no signals were generated or data is insufficient.")

        else:
            st.warning("Cannot run backtest: Chart data is not available or empty.")

    with st.expander("See Selected Inputs"):
        st.json(inputs)

with sandbox_tab:
    render_technical_sandbox_ui(cache=cache, yf=yf_service, start_date=start_date, end_date=end_date)
