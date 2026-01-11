"""
UI components for the Strategy Backtester.
"""
import streamlit as st
from src.config.constants import YFINANCE_TICKERS, FRED_SERIES

def render_backtester_inputs():
    """
    Renders the input widgets for the strategy backtester.
    """
    inputs = {}
    parameters = {}

    st.subheader("Strategy Configuration")

    # --- Equity Selection ---
    col1, col2 = st.columns(2)
    with col1:
        yfinance_options = {ticker: f"{config['name']} ({ticker})" for ticker, config in YFINANCE_TICKERS.items()}
        yfinance_options["Other"] = "Enter Custom Ticker"
        
        selected_equity = st.selectbox(
            "Select Equity Instrument",
            options=list(yfinance_options.keys()),
            format_func=lambda x: yfinance_options[x],
            index=0
        )
        if selected_equity == "Other":
            equity = st.text_input("Enter Custom Ticker", "^GSPC")
        else:
            equity = selected_equity
    
    inputs["equity"] = equity

    # --- Signal Selection ---
    with col2:
        signals = st.multiselect(
            "Select Signal Indicators",
            options=["VIX", "Yield Curve", "GDP", "RSI", "Moving Average Crossover"],
            default=["RSI"],
            help="Choose the indicators to generate trading signals."
        )
    inputs["signals"] = signals

    # --- Signal Parameters ---
    st.subheader("Signal Parameters")
    
    if not signals:
        st.info("Select one or more signal indicators to configure their parameters.")

    if "VIX" in signals:
        with st.expander("VIX Parameters", expanded=True):
            parameters['vix_threshold'] = st.number_input("VIX Threshold", min_value=0, value=30, help="Signal triggers when VIX is above this value.")

    if "Yield Curve" in signals:
         with st.expander("Yield Curve Parameters", expanded=True):
            col1, col2 = st.columns(2)
            treasury_options = {
                series_id: config["name"]
                for series_id, config in FRED_SERIES.items()
                if config["category"] == "Interest Rates"
            }
            
            with col1:
                parameters['yield_curve_short'] = st.selectbox(
                    "Short-Term Rate",
                    options=list(treasury_options.keys()),
                    format_func=lambda x: treasury_options[x],
                    index=list(treasury_options.keys()).index("DGS2") # Default to 2-Year
                )
            with col2:
                parameters['yield_curve_long'] = st.selectbox(
                    "Long-Term Rate",
                    options=list(treasury_options.keys()),
                    format_func=lambda x: treasury_options[x],
                    index=list(treasury_options.keys()).index("DGS10") # Default to 10-Year
                )

    if "RSI" in signals:
        with st.expander("RSI Parameters", expanded=True):
            parameters['rsi_length'] = st.number_input("RSI Length", min_value=1, max_value=100, value=14)
            parameters['rsi_oversold'] = st.number_input("RSI Oversold Level", min_value=0, max_value=100, value=30)
            parameters['rsi_overbought'] = st.number_input("RSI Overbought Level", min_value=0, max_value=100, value=70)

    if "Moving Average Crossover" in signals:
        with st.expander("Moving Average Crossover Parameters", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                parameters['ma_short'] = st.number_input("Short MA Period", min_value=1, max_value=100, value=20)
            with col2:
                parameters['ma_long'] = st.number_input("Long MA Period", min_value=1, max_value=200, value=50)

    inputs["parameters"] = parameters
    
    # --- Backtest Parameters ---
    st.subheader("Backtest Parameters")
    inputs["forward_return_period"] = st.number_input("Forward Return Period (Days)", min_value=1, value=30)

    st.divider()
    
    inputs["run_backtest"] = st.button("▶️ Run Backtest", use_container_width=True, type="primary")

    return inputs
