# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based portfolio webapp showcasing quantitative and qualitative financial research. The app integrates multiple data sources (FRED, Stats Canada, yfinance) with Firebase/Firestore for intelligent caching and features interactive equity analysis tools.

**Core Philosophy:** Prioritize readability over cleverness. Ask clarifying questions before making architectural changes.

## Development Commands

```bash
# Activate virtual environment (Windows)
Bash(ls .venv/Scripts/

# Run Streamlit webapp locally (from project root)
Bash(.venv/Scripts/streamlit.exe run Home.py)

# Add packages (use uv package manager)
uv add <package-name>
```

## Project Architecture

### Multi-Tier Data Architecture

The app uses a separation of concerns pattern where data storage is split across Firebase services:

- **Firestore**: Stores lightweight metadata only (release dates, schemas, row counts, update timestamps)
- **Cloud Storage**: Stores actual data files in Parquet format (respects Firestore's 1MB document limit)

This dual-storage pattern must be maintained when extending to new data sources (FRED, yfinance, etc.).

### Configuration and Secrets Management

**Critical:** ALL credentials and API keys MUST be loaded from `.streamlit/secrets.toml` via `st.secrets`. Never hardcode credentials.

```python
# ✅ CORRECT
import streamlit as st
api_key = st.secrets["fred"]["api_key"]

# ❌ WRONG - Never hardcode
api_key = "abc123xyz"
```

Expected secrets structure:
- `[fred]` - FRED API configuration
- `[gcp_service_account]` - Firebase/GCP service account JSON
- `[firebase]` - Storage bucket configuration
- `[google_oauth]` - Google OAuth credentials (Phase 2+)
- `[app]` - Application config (admin_email: waqar.qureshi.uoft@gmail.com)

Configuration loading should be centralized in `src/config/settings.py` with functions like `get_firebase_config()`, `get_fred_config()`, etc.

### Storage Path Convention

Data files follow this pattern: `{data_source}/{identifier}/{date}.parquet`

Examples:
- `fred/DGS10/2024-12-01.parquet`
- `statscan/36100434/2024-11-15.parquet`
- `yfinance/AAPL/2024-12-08.parquet`

### Smart Caching Strategy

The cache manager (`src/data/cache_manager.py`) implements get-or-fetch logic:
1. Check Firestore metadata for existing data and last update timestamp
2. If cached and recent, retrieve from Cloud Storage
3. If stale or missing, fetch from API, save to Cloud Storage, update Firestore metadata
4. Return Polars DataFrame

This pattern should be followed for all data sources.

### Authentication & Authorization

- Google OAuth for user authentication (Phase 2+)
- Admin access: Only `waqar.qureshi.uoft@gmail.com` gets database management controls
- Admin detection via `src/auth/permissions.py` using `is_admin()` function
- Session state managed through `src/auth/google_auth.py`

## Code Standards

- **Type hints required** on all function signatures for readability
- **Polars preferred** for DataFrame operations (over pandas)
- **Interactive visualizations** using Plotly for all charts
- Functions should follow single responsibility principle

## Project Structure

```
portfolio/
  archive/v1/                 # Previous implementation (reference only)
  Home.py                     # Entry point
  pages/                      # Streamlit pages
    1_Analysis.py             # FRED/Stats Canada/yfinance visualizations
    2_Equity_Playroom.py      # 4 interactive equity tools (tabs)
  src/
    config/                   # settings.py (secrets loader), constants.py
    services/                 # API clients: firebase_service, fred_api, statscan_api, yfinance_service
    auth/                     # google_auth.py, permissions.py
    data/                     # cache_manager.py, *_datasets.py (configs)
    components/               # Reusable UI: charts.py, sidebar.py, auth_ui.py, admin.py
    tools/                    # Equity Playroom tools (each is a package with ui.py)
      strategy_backtester/
      equity_simulator/
      returns_explorer/
      technical_sandbox/
```

## Phased Implementation Plan
The project follows a comprehensive 10-phase plan.

Primary Source of Truth: All current task details, status ([ ] or [x]), and next steps are exclusively managed in the PROJECT_TASKS.md file in the project root.

PLease refer to /conductor/tracks to see the various plans in play with the relevant tasks that need to be completed and marked as completed.

## Data Source Specifics

### FRED (Federal Reserve Economic Data)
- Series examples: DGS10 (10Y Treasury), DGS2 (2Y Treasury), CPIAUCSL (CPI), GDPC1 (GDP), HOUST (Housing Starts)
- Use `fredapi` package
- API key from `st.secrets["fred"]["api_key"]`

### Stats Canada
- Uses Product IDs (PIDs) like "36100434"
- Existing implementation pattern in `archive/v1/functions/statscan_api.py`
- Returns data with geographic/industry breakdowns

### yfinance
- Equity market data for ticker symbols
- Historical price data, company info
- Cache by ticker symbol and date range

## Firebase Project Details

- Project ID: `portfolio-64bae`
- Storage bucket: `portfolio-64bae.appspot.com`
- Firestore in Native mode
- Service account credentials required in secrets.toml