"""
UI components for the Technical Sandbox.
"""
import streamlit as st
import polars as pl
from datetime import date
from typing import List, Dict

from src.data.cache_manager import CacheManager
from src.services.yfinance_service import YFinanceService
from src.tools.technical_sandbox.indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_macd
from src.tools.strategy_backtester.plots import render_price_chart_with_indicators # Reuse for now
from src.config.constants import YFINANCE_TICKERS

def render_technical_sandbox_ui(cache: CacheManager, yf: YFinanceService, start_date: date, end_date: date):
    """
    Renders the UI for the Technical Sandbox, including inputs, data fetching, and charting.
    """
    st.header("Interactive Technical Analysis")

    # --- Equity Selection ---
    col1, col2 = st.columns(2)
    with col1:
        yfinance_options = {ticker: f"{config['name']} ({ticker})" for ticker, config in YFINANCE_TICKERS.items()}
        yfinance_options["Other"] = "Enter Custom Ticker"
        
        selected_equity = st.selectbox(
            "Select Equity Instrument",
            options=list(yfinance_options.keys()),
            format_func=lambda x: yfinance_options[x],
            index=0,
            key="sandbox_equity_select"
        )
        if selected_equity == "Other":
            equity_ticker = st.text_input("Enter Custom Ticker", "^GSPC", key="sandbox_custom_ticker")
        else:
            equity_ticker = selected_equity
    
    # --- Indicator Selection ---
    with col2:
        selected_indicators = st.multiselect(
            "Select Technical Indicators",
            options=["SMA", "EMA", "RSI", "MACD"],
            default=["SMA", "RSI"],
            key="sandbox_indicators_select"
        )

    indicator_params = {}
    st.subheader("Indicator Parameters")

    if "SMA" in selected_indicators:
        with st.expander("SMA Parameters", expanded=True):
            indicator_params['sma_period'] = st.number_input("SMA Period", min_value=1, value=50, key="sandbox_sma_period")
    
    if "EMA" in selected_indicators:
        with st.expander("EMA Parameters", expanded=True):
            indicator_params['ema_period'] = st.number_input("EMA Period", min_value=1, value=50, key="sandbox_ema_period")

    if "RSI" in selected_indicators:
        with st.expander("RSI Parameters", expanded=True):
            indicator_params['rsi_period'] = st.number_input("RSI Period", min_value=1, value=14, key="sandbox_rsi_period")
            indicator_params['rsi_oversold'] = st.number_input("RSI Oversold Level", min_value=0, max_value=100, value=30, key="sandbox_rsi_oversold")
            indicator_params['rsi_overbought'] = st.number_input("RSI Overbought Level", min_value=0, max_value=100, value=70, key="sandbox_rsi_overbought")

    if "MACD" in selected_indicators:
        with st.expander("MACD Parameters", expanded=True):
            col_macd1, col_macd2, col_macd3 = st.columns(3)
            with col_macd1:
                indicator_params['macd_fastperiod'] = st.number_input("Fast Period", min_value=1, value=12, key="sandbox_macd_fast")
            with col_macd2:
                indicator_params['macd_slowperiod'] = st.number_input("Slow Period", min_value=1, value=26, key="sandbox_macd_slow")
            with col_macd3:
                indicator_params['macd_signalperiod'] = st.number_input("Signal Period", min_value=1, value=9, key="sandbox_macd_signal")
    
    st.divider()

    # --- Fetch Data and Calculate Indicators ---
    if equity_ticker:
        with st.spinner(f"Fetching data for {equity_ticker} and calculating indicators..."):
            equity_df = cache.get_or_fetch(
                source="yfinance",
                source_id=equity_ticker,
                fetch_fn=lambda: yf.get_ticker_history(equity_ticker, start=start_date, end=end_date),
                frequency="daily",
                metadata_fn=lambda: {"ticker": equity_ticker, "name": equity_ticker},
                force_refresh=False
            )
            
            if not equity_df.is_empty():
                # Apply selected indicators
                df_with_indicators = equity_df.clone() # Use clone to avoid modifying original cached df
                
                if "SMA" in selected_indicators:
                    df_with_indicators = calculate_sma(df_with_indicators, indicator_params['sma_period'])
                if "EMA" in selected_indicators:
                    df_with_indicators = calculate_ema(df_with_indicators, indicator_params['ema_period'])
                if "RSI" in selected_indicators:
                    df_with_indicators = calculate_rsi(df_with_indicators, indicator_params['rsi_period'])
                if "MACD" in selected_indicators:
                    df_with_indicators = calculate_macd(
                        df_with_indicators,
                        fastperiod=indicator_params['macd_fastperiod'],
                        slowperiod=indicator_params['macd_slowperiod'],
                        signalperiod=indicator_params['macd_signalperiod']
                    )

                # --- Plotting ---
                # This will need to be a custom plotting function for the sandbox
                # For now, let's adapt render_price_chart_with_indicators
                
                # The 'signals' parameter in render_price_chart_with_indicators is for backtester signals,
                # not for general indicators. We need to pass the indicator columns separately.
                # Let's just create a very simple plot here for now or update render_price_chart_with_indicators
                # to be more generic. For simplicity, let's just make a basic plot.

                # Simple plot for now
                fig = render_price_chart_with_indicators(
                    df=df_with_indicators,
                    equity_ticker=equity_ticker,
                    signals=[], # No backtester signals
                    params=indicator_params # Pass indicator params for RSI overbought/oversold lines
                )
                
                # Manually add other indicator traces if render_price_chart_with_indicators doesn't handle them
                # This is a temporary measure until a proper sandbox plotting function is created.
                if "EMA" in selected_indicators:
                    fig.add_trace(go.Scatter(x=df_with_indicators["date"], y=df_with_indicators[f"ema_{indicator_params['ema_period']}"], name=f"EMA({indicator_params['ema_period']})", mode='lines'), row=1, col=1)
                
                # MACD needs its own subplot or a more complex overlay
                if "MACD" in selected_indicators:
                    # MACD typically has its own subplot.
                    # This requires modifying render_price_chart_with_indicators or creating a new plot function.
                    st.warning("MACD plotting not fully integrated yet. Will display separately for now.")
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(x=df_with_indicators["date"], y=df_with_indicators["macd"], name="MACD", mode='lines'))
                    fig_macd.add_trace(go.Scatter(x=df_with_indicators["date"], y=df_with_indicators["macdsignal"], name="Signal Line", mode='lines'))
                    fig_macd.add_trace(go.Bar(x=df_with_indicators["date"], y=df_with_indicators["macdhist"], name="Histogram"))
                    fig_macd.update_layout(title_text=f"{equity_ticker} MACD", hovermode="x unified")
                    st.plotly_chart(fig_macd, use_container_width=True)

                st.plotly_chart(fig, use_container_width=True)


            else:
                st.warning(f"Could not fetch data for '{equity_ticker}'.")

    else:
        st.info("Enter an equity ticker to start.")
