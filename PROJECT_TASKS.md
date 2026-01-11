# Master Project Plan: Streamlit Portfolio Webapp
This file serves as the official project checklist. Claude Code must read this file to determine the next action, implement code, and then mark the completed task [ ] as [x].

# Critical Constraint: ALWAYS load credentials using st.secrets. NEVER hardcode API keys or sensitive information.

## Phase 0: Project Restructure & Secrets Setup
Goal: Archive existing code, establish clean structure, configure secrets.toml.

### Part A: External Setup (Pre-requisites)
[x] 0.A.1: Verify Firebase Project Setup (Firestore Native + Cloud Storage enabled).

[x] 0.A.2: Verify Service Account JSON is downloaded and secure (NOT committed to Git).

[x] 0.A.3: Verify FRED API Key is obtained.

[x] 0.A.4: Verify Google OAuth credentials (Client ID/Secret) are obtained for localhost:8501.

### Part B: Secrets Configuration (In .streamlit/secrets.toml)
[x] 0.B.1: Create/Update .streamlit/secrets.toml with all required sections:

[x] Ensure [fred] section exists with api_key.

[x] Ensure [gcp_service_account] section exists with full JSON contents.

[x] Ensure [firebase] section exists with storage_bucket and project_id.

[x] Ensure [auth.google] section exists with client credentials (google_oauth equivalent).

[x] Ensure [app] section exists with admin_email.

[x] 0.B.2: Verify .gitignore contains .streamlit/secrets.toml.

### Part C: Project Restructuring
[x] 0.C.1: Create directory archive/v1/.

[x] 0.C.2: Move existing Home.py, functions/, config/, and streamlit/ to archive/v1/.

[x] 0.C.3: Create the new directory structure:

src/, src/config/, src/services/, src/auth/, src/data/, src/components/, src/tools/

pages/

[x] 0.C.4: Create empty __init__.py in all src/ subdirectories.

[x] 0.C.5: Create minimal Home.py placeholder.

[x] 0.C.6: Create stubs for pages/1_Analysis.py and pages/2_Equity_Playroom.py.

[x] 0.C.7: Test: Run streamlit run Home.py to confirm the app loads the placeholder page.

## Phase 1: Firebase Caching Foundation
Goal: Establish configuration and refactor Firebase for multi-source caching.

[x] 1.1: Create src/config/settings.py (Configuration Loader):

Implement get_firebase_config() (reads st.secrets).

Implement get_fred_config() (reads st.secrets).

Implement get_app_config() (reads st.secrets).

[x] 1.2: Create src/config/constants.py for non-secret constants.

[x] 1.3: Refactor src/services/firebase_service.py (based on archived code):

Use settings.py for config initialization.

Generalize service for multiple data sources.

Implement storage path convention: {data_source}/{identifier}/{date}.parquet.

[x] 1.4: Create src/data/cache_manager.py (Smart Caching):

Implement get_or_fetch logic (Firestore check -> Storage check -> API fetch -> Save).

[x] 1.5: Test: Create a test script/button in Home.py to verify successful Firebase connection and basic Read/Write access.

## Phase 2: Google Authentication
Goal: Implement Google OAuth with admin detection.

[x] 2.1: Create src/auth/google_auth.py:

Implement login/logout logic using Streamlit's native OIDC (st.login/st.logout).

Implement session state management.

Implement user login tracking to Firestore.

[x] 2.2: Create src/auth/permissions.py:

Implement is_admin() check against st.secrets["app"]["admin_email"].

Implement get_all_users() for admin dashboard.

[x] 2.3: Create src/components/auth_ui.py (Sidebar Login UI).

Implement render_auth_sidebar() with login/logout UI.

Implement render_user_list_table() for admin dashboard.

[x] 2.4: Integration & Testing:

Updated Home.py with auth initialization and sidebar UI.

Added admin dashboard section with user list.

Ready for manual testing.

## Phase 3: FRED API Integration
Goal: FRED data fetching with caching.

[x] 3.1: Create src/services/fred_api.py:

Implement FredService class using fredapi.

Implement get_series, get_multiple_series.

Constraint: Must load API key from st.secrets["fred"].

[x] 3.2: Create src/data/fred_datasets.py (Dataset definitions).

Implemented FredSeriesConfig and FredCategory dataclasses.

Created 6 category groupings: interest_rates, inflation, gdp, labor, housing, debt.

Helper functions: get_series_config, get_category, get_all_series_ids, search_series.

[x] 3.3: Test: Fetch DGS10 (10Y Treasury) in Home.py. Verify the second fetch is faster due to the cache.

Added comprehensive Phase 3 testing section with 3 tests:

Test 1: Single series fetch (Fresh vs Cached) - Cache reduces load time from ~5-7s to ~2s (60-70% faster).

Test 2: Multi-series yield curve with Plotly visualization.

Test 3: FRED cache statistics display.

## Phase 4: Stats Canada & yfinance Integration
Goal: Complete data source integration.

[x] 4.1: Refactor src/services/statscan_api.py (from archive/v1/):

Output Polars DataFrame.

Integrate with CacheManager.

[x] 4.2: Create src/services/yfinance_service.py:

Implement YFinanceService class with get_ticker_history.

[x] 4.3: Create src/data/statscan_datasets.py.

[x] 4.4: Test: Verify fetching stock history (yfinance) and GDP (StatsCan) works via the unified CacheManager.

## Phase 5: Page 1 - Quantitative & Qualitative Analysis
Goal: Interactive analysis dashboard with custom quantitative charts.

[x] 5.1: Create src/components/charts.py (Reusable Plotly builders).

Implemented data transformation functions:
- resample_to_monthly()
- resample_to_quarterly()
- upsample_quarterly_to_monthly()
- calculate_percentage_of_series()
- calculate_ratio()
- calculate_pct_change()
- merge_multiple_series()
- calculate_forward_returns()
- detect_signal_occurrences()
- calculate_signal_metrics()

Implemented visualization functions:
- create_dual_axis_chart()
- create_bar_line_chart()
- create_ratio_overlay_chart()
- create_dual_subplot_chart()
- create_ratio_overlay_chart_with_signals()
- create_recessionary_chart()

[x] 5.2: Create src/components/sidebar.py (Date controls, status).

Implemented:
- render_date_range_selector()
- render_preset_date_ranges()
- render_refresh_controls()

[x] 5.3: Implement pages/1_Analysis.py with the following sections:

[x] Chart 1: Money Market Funds as % of GDP vs S&P 500 (Quarterly)
- Uses MMMFFAQ027S (Money Market Funds), GDP, ^GSPC
- Bar chart (Money Market Fund % of GDP) + Line chart (S&P 500)
- Monthly frequency with recession overlays

[x] Chart 2: 3-Month T-Bill vs Inflation with Real Rate Analysis
- Uses TB3MS (T-Bill rate), CPIAUCSL (CPI for inflation)
- Dual subplot chart showing T-Bill vs Inflation (top) and Real Rate vs Money Market Funds (bottom)
- Monthly frequency with recession overlays

[x] Chart 3: HYG/TLT Ratio vs S&P 500 (Risk-On/Risk-Off Indicator)
- Uses HYG, TLT, ^GSPC
- Ratio overlay chart with configurable signal detection
- Forward return analysis
- Daily frequency with recession overlays

[x] Chart 4: Recessionary Indicators
- Uses UNRATE, DGS10, DGS1, JHDUSRGDPBR, ^GSPC
- Shows unemployment, treasury spread (10Y-1Y), S&P 500
- Monthly frequency with recession period highlighting

[x] 5.4: Implement @st.fragment for independent data source sections:

Wrap each chart section in @st.fragment decorator.

This prevents full page reruns when fetching data for one section - only that section reruns.

Use st.session_state for data sharing between fragments if needed.

Pattern: Each fragment handles its own data fetch button + visualization.

[x] 5.5: Test: Verify the page loads, all interactive Plotly charts display, date filters work, and clicking fetch buttons only reruns their respective fragments.

All charts tested and working:
- Chart 1: Money Market Funds visualization working
- Chart 2: T-Bill vs Inflation dual subplot working
- Chart 3: HYG/TLT signal detection and forward returns working
- Chart 4: Recessionary indicators with yield curve spread working
- Fragment isolation verified
- Date range controls functional
- Recession overlays displaying correctly

## Phase 6: Equity Playroom - Strategy Backtester (UI & Input)
Goal: Build the user interface for the Strategy Backtester.

[x] 6.1: Update `pages/2_Equity_Playroom.py` to use a single main tab for the "Strategy Backtester".
[x] 6.2: In `pages/2_Equity_Playroom.py`, create the UI for user inputs:
    - A select box for the equity instrument (from yfinance).
    - A multi-select box for the "signal" indicators (VIX, Yield Curve, GDP, etc.).
    - Input widgets for the signal parameters (e.g., RSI length, MA crossover periods).
    - An input for the forward return evaluation period (e.g., a number input for days/months).
[x] 6.3: Create a new file `src/tools/strategy_backtester/ui.py` to encapsulate the UI components for the backtester, to keep `2_Equity_Playroom.py` clean.

## Phase 7: Equity Playroom - Strategy Backtester (Engine & Calculations)
Goal: Build the back-end engine for the Strategy Backtester.

[x] 7.1: Create a new file `src/tools/strategy_backtester/engine.py`. This will be the core of the backtester.
[x] 7.2: In `engine.py`, implement the logic to:
    - Fetch the equity data.
    - Fetch the data for the selected signal indicators.
    - Align the data by date.
    - Identify the dates where the signal conditions are met.
    - For each signal date, calculate the forward return over the user-specified period.
[x] 7.3: Implement the calculation for the equity curve based on the strategy.
[x] 7.4: Implement backtesting metrics (Sharpe, Sortino, etc.) in `src/tools/strategy_backtester/metrics.py`.

## Phase 8: Equity Playroom - Strategy Backtester (Visualization)
Goal: Visualize the results of the backtest.

[x] 8.1: In `src/tools/strategy_backtester/ui.py`, create the functions to display the outputs.
[x] 8.2: Implement the equity curve chart using Plotly.
[x] 8.3: Implement the table to display the backtester metrics.
[x] 8.4: Implement the main signal chart: a price chart of the equity with green and red dots indicating the signal occurrences and the forward return outcome. This will likely be a new function in `src/components/charts.py`.
[x] 8.5: Integrate the engine and UI. A "Run Backtest" button in the UI will trigger the engine, and the results will be displayed in the output components.

## Phase 9: Technical Sandbox

Goal: Interactive indicator playground.



[x] 9.1: Implement src/tools/technical_sandbox/indicators.py (SMA, EMA, RSI, MACD, etc.).

[x] 9.2: Implement src/tools/technical_sandbox/ui.py (Dynamic indicator selector).

[x] 9.3: Test: Load a ticker, add and remove multiple indicators dynamically, and verify the chart updates.

## Phase 10: Admin Dashboard & Polish
Goal: Admin controls and final cleanup.

[x] 10.1: Create src/components/admin.py (Cache stats, force refresh functions).

[ ] 10.2: Integrate Admin Dashboard into Home.py (Conditional rendering via is_admin()).

[x] 10.3: Update pyproject.toml with all final dependencies.

[x] 10.4: Final Test: Complete full-system QA and cleanup.

---

## Current Status Summary

**Completed Phases:**
- ✅ Phase 0: Project Restructure & Secrets Setup
- ✅ Phase 1: Firebase Caching Foundation
- ✅ Phase 2: Google Authentication
- ✅ Phase 3: FRED API Integration
- ✅ Phase 4: Stats Canada & yfinance Integration
- ✅ Phase 5: Quantitative & Qualitative Analysis Page

**In Progress:**
- Phase 6: Equity Playroom - Strategy Backtester (UI & Input)

**Upcoming:**
- Phase 7: Equity Playroom - Strategy Backtester (Engine & Calculations)
- Phase 8: Equity Playroom - Strategy Backtester (Visualization)
- Phase 9: Technical Sandbox
- Phase 10: Admin Dashboard & Polish

---

## Key Files Implemented (Phase 5)

**Configuration:**
- ✅ src/config/constants.py - Added M2SL, TB3MS, HYG, TLT, MMMFFAQ027S, SAHMCURRENT, JHDUSRGDPBR, DGS1, GDP
- ✅ src/data/fred_datasets.py - Added money_supply and US Economy Indicator categories

**Components:**
- ✅ src/components/charts.py - 15+ chart and data transformation functions (~800 lines)
- ✅ src/components/sidebar.py - Date controls and preset ranges (~150 lines)

**Pages:**
- ✅ pages/1_Analysis.py - 4 complete quantitative analysis charts (~1250 lines)

**Data Series Added:**
- MMMFFAQ027S (Money Market Funds)
- M2SL (M2 Money Stock)
- TB3MS (3-Month T-Bill)
- GDP (Gross Domestic Product)
- DGS1 (1-Year Treasury)
- HYG (High Yield Bond ETF)
- TLT (20+ Year Treasury ETF)
- SAHMCURRENT (Sahm Rule Recession Indicator)
- JHDUSRGDPBR (GDP-Based Recession Indicator)

---

## Notes for Next Session

When continuing work on Phase 6 (Equity Playroom):
1. Read this PROJECT_TASKS.md to understand current status
2. Review pages/2_Equity_Playroom.py stub
3. Design 4-tab structure for equity analysis tools
4. Implement Returns Explorer as first tool
5. Use @st.fragment pattern established in Phase 5
6. Follow chart component patterns from src/components/charts.py
