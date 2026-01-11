"""
Equity Value Playroom
Interactive tools for equity analysis and strategy testing
"""
import streamlit as st
from src.tools.strategy_backtester.ui import render_backtester_inputs

st.set_page_config(
    page_title="Equity Playroom | Portfolio",
    page_icon="🎮",
    layout="wide"
)

st.title("📈 Strategy Backtester")

st.info("This tool allows you to build and backtest custom trading strategies based on a variety of technical and economic indicators.")

inputs = render_backtester_inputs()

if inputs["run_backtest"]:
    st.write("Running backtest with the following inputs:")
    st.json(inputs)
