# Plan for Track: Phase 6: Equity Playroom - Strategy Backtester (UI & Input)

This plan outlines the steps to build the user interface for the Strategy Backtester within the Equity Playroom.

## Phase 1: Initial UI Setup and Widget Integration

### Tasks

- [ ] Task: Create the basic Streamlit UI structure for the Strategy Backtester in `src/tools/strategy_backtester/ui.py`.
- [ ] Task: Add a multi-select widget for selecting stock tickers.
- [ ] Task: Add a date input widget for defining the backtest period (start and end dates).
- [ ] Task: Add a numeric input for initial capital.
- [ ] Task: Add a dropdown for strategy selection (e.g., "Moving Average Crossover", "RSI Trading").
- [ ] Task: Add input widgets for strategy parameters (e.g., short_window, long_window for Moving Average). These should be dynamically displayed based on strategy selection.
- [ ] Task: Add a button to trigger the backtest.