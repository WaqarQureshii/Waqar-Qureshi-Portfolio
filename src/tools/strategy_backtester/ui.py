"""
UI components for the Strategy Backtester.
"""
import streamlit as st

def render_backtester_inputs():
    """
    Renders the input widgets for the strategy backtester.
    """
    st.subheader("Strategy Configuration")

    # Equity selection
    equity = st.text_input("Equity Ticker", "^GSPC", help="Enter a Yahoo Finance ticker.")

    # Signal selection
    signals = st.multiselect(
        "Select Signal Indicators",
        options=["VIX", "Yield Curve", "GDP", "RSI", "Moving Average Crossover"],
        default=["RSI"],
        help="Choose the indicators to generate trading signals."
    )

    # Signal parameters
    st.subheader("Signal Parameters")
    
    parameters = {}

    if "RSI" in signals:
        parameters['rsi_length'] = st.number_input("RSI Length", min_value=1, max_value=100, value=14)

    if "Moving Average Crossover" in signals:
        parameters['ma_short'] = st.number_input("Short MA Period", min_value=1, max_value=100, value=20)
        parameters['ma_long'] = st.number_input("Long MA Period", min_value=1, max_value=200, value=50)

    # Evaluation period
    st.subheader("Backtest Parameters")
    forward_return_period = st.number_input("Forward Return Period (Days)", min_value=1, value=30)

    run_backtest = st.button("Run Backtest")

    return {
        "equity": equity,
        "signals": signals,
        "parameters": parameters,
        "forward_return_period": forward_return_period,
        "run_backtest": run_backtest
    }
