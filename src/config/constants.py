"""
Non-secret constants for portfolio webapp.

This file contains configuration values that are NOT sensitive:
- Collection names
- Storage paths
- Dataset identifiers
- Retention policies
- Display settings

NEVER put API keys, passwords, or tokens in this file.
All credentials belong in .streamlit/secrets.toml (loaded via settings.py)
"""

from typing import List, Dict

# =============================================================================
# FIRESTORE COLLECTIONS
# =============================================================================

# FRED data collections
FRED_METADATA_COLLECTION = "fred_metadata"
FRED_UPDATE_LOGS_COLLECTION = "fred_update_logs"

# yfinance data collections
YFINANCE_METADATA_COLLECTION = "yfinance_metadata"
YFINANCE_UPDATE_LOGS_COLLECTION = "yfinance_update_logs"

# Stats Canada data collections
STATSCAN_METADATA_COLLECTION = "statscan_metadata"
STATSCAN_UPDATE_LOGS_COLLECTION = "statscan_update_logs"

# =============================================================================
# CLOUD STORAGE PATHS
# =============================================================================

# Storage path prefixes (used in path construction)
FRED_STORAGE_PREFIX = "fred"
YFINANCE_STORAGE_PREFIX = "yfinance"
STATSCAN_STORAGE_PREFIX = "statscan"

# File format
DATA_FILE_FORMAT = "parquet"  # Use Parquet for all data storage

# =============================================================================
# RETENTION POLICIES
# =============================================================================

# Keep last N versions of each dataset before cleanup
KEEP_VERSIONS = 3

# Cache freshness thresholds (in hours)
# Data is considered stale if older than these thresholds
FRESHNESS_THRESHOLDS = {
    "fred": {
        "daily": 24,      # Daily series: refresh after 24 hours
        "weekly": 168,    # Weekly series: refresh after 7 days
        "monthly": 720,   # Monthly series: refresh after 30 days
        "quarterly": 2160, # Quarterly series: refresh after 90 days
        "annual": 8760    # Annual series: refresh after 365 days
    },
    "yfinance": {
        "1d": 24,         # Daily data: refresh after 24 hours
        "1wk": 168,       # Weekly data: refresh after 7 days
        "1mo": 720        # Monthly data: refresh after 30 days
    },
    "statscan": {
        "daily": 24,
        "weekly": 168,
        "monthly": 720,
        "quarterly": 2160,
        "annual": 8760
    }
}

# =============================================================================
# FRED SERIES TO TRACK
# =============================================================================

# Key economic indicators from FRED
FRED_SERIES: Dict[str, Dict[str, str]] = {
    # Treasury Yields
    "DGS10": {
        "name": "10-Year Treasury Constant Maturity Rate",
        "category": "Interest Rates",
        "frequency": "daily",
        "priority": 1
    },
    "DGS2": {
        "name": "2-Year Treasury Constant Maturity Rate",
        "category": "Interest Rates",
        "frequency": "daily",
        "priority": 1
    },
    "DGS5": {
        "name": "5-Year Treasury Constant Maturity Rate",
        "category": "Interest Rates",
        "frequency": "daily",
        "priority": 2
    },
    "DGS30": {
        "name": "30-Year Treasury Constant Maturity Rate",
        "category": "Interest Rates",
        "frequency": "daily",
        "priority": 2
    },

    # Inflation
    "CPIAUCSL": {
        "name": "Consumer Price Index for All Urban Consumers",
        "category": "Inflation",
        "frequency": "monthly",
        "priority": 1
    },
    "CPILFESL": {
        "name": "CPI: All Items Less Food & Energy",
        "category": "Inflation",
        "frequency": "monthly",
        "priority": 2
    },

    # GDP
    "GDPC1": {
        "name": "Real Gross Domestic Product",
        "category": "GDP",
        "frequency": "quarterly",
        "priority": 1
    },

    # Labor Market
    "UNRATE": {
        "name": "Unemployment Rate",
        "category": "Labor",
        "frequency": "monthly",
        "priority": 1
    },
    "PAYEMS": {
        "name": "All Employees: Total Nonfarm",
        "category": "Labor",
        "frequency": "monthly",
        "priority": 1
    },

    # Housing
    "HOUST": {
        "name": "Housing Starts: Total New Privately Owned",
        "category": "Housing",
        "frequency": "monthly",
        "priority": 1
    },
    "CSUSHPISA": {
        "name": "S&P/Case-Shiller U.S. National Home Price Index",
        "category": "Housing",
        "frequency": "monthly",
        "priority": 2
    },

    # Debt
    "GFDEBTN": {
        "name": "Federal Debt: Total Public Debt",
        "category": "Debt",
        "frequency": "quarterly",
        "priority": 2
    },
    "TDSP": {
        "name": "Household Debt Service Payments",
        "category": "Debt",
        "frequency": "quarterly",
        "priority": 2
    }
}

# =============================================================================
# YFINANCE TICKERS TO TRACK
# =============================================================================

YFINANCE_TICKERS: Dict[str, Dict[str, str]] = {
    # Major Indices
    "^GSPC": {
        "name": "S&P 500",
        "category": "Index",
        "sector": "Market",
        "interval": "1d",
        "priority": 1
    },
    "^DJI": {
        "name": "Dow Jones Industrial Average",
        "category": "Index",
        "sector": "Market",
        "interval": "1d",
        "priority": 1
    },
    "^IXIC": {
        "name": "NASDAQ Composite",
        "category": "Index",
        "sector": "Market",
        "interval": "1d",
        "priority": 1
    },
    "^VIX": {
        "name": "CBOE Volatility Index",
        "category": "Volatility",
        "sector": "Market",
        "interval": "1d",
        "priority": 1
    },

    # Major Tech Stocks
    "AAPL": {
        "name": "Apple Inc.",
        "category": "Stock",
        "sector": "Technology",
        "interval": "1d",
        "priority": 2
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "category": "Stock",
        "sector": "Technology",
        "interval": "1d",
        "priority": 2
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "category": "Stock",
        "sector": "Technology",
        "interval": "1d",
        "priority": 2
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "category": "Stock",
        "sector": "Consumer Cyclical",
        "interval": "1d",
        "priority": 2
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "category": "Stock",
        "sector": "Technology",
        "interval": "1d",
        "priority": 2
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "category": "Stock",
        "sector": "Consumer Cyclical",
        "interval": "1d",
        "priority": 2
    }
}

# =============================================================================
# STATS CANADA PRODUCT IDS TO TRACK
# =============================================================================

# Referencing the existing dataset configurations from archive
# These will be fully defined in src/data/statscan_datasets.py
STATSCAN_PRIORITY_TABLES: List[str] = [
    "36100434",  # GDP by industry (monthly)
    "36100222",  # GDP by expenditure (quarterly)
    "18100004",  # CPI
    "10100139",  # Interest rates
    "14100287",  # Employment
    "34100143",  # Housing starts
    "18100205",  # Housing prices
    "12100011",  # International trade
]

# =============================================================================
# DATA SOURCE CATEGORIES
# =============================================================================

DATA_SOURCES = {
    "fred": {
        "name": "Federal Reserve Economic Data",
        "description": "US economic and financial data from FRED",
        "url": "https://fred.stlouisfed.org/"
    },
    "yfinance": {
        "name": "Yahoo Finance",
        "description": "Stock market data and equity information",
        "url": "https://finance.yahoo.com/"
    },
    "statscan": {
        "name": "Statistics Canada",
        "description": "Canadian economic and demographic data",
        "url": "https://www.statcan.gc.ca/"
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_collection_names(source: str) -> Dict[str, str]:
    """
    Get Firestore collection names for a data source.

    Args:
        source: Data source identifier ("fred", "yfinance", "statscan")

    Returns:
        dict: Collection names {"metadata": str, "logs": str}

    Raises:
        ValueError: If source is not recognized
    """
    collections = {
        "fred": {
            "metadata": FRED_METADATA_COLLECTION,
            "logs": FRED_UPDATE_LOGS_COLLECTION
        },
        "yfinance": {
            "metadata": YFINANCE_METADATA_COLLECTION,
            "logs": YFINANCE_UPDATE_LOGS_COLLECTION
        },
        "statscan": {
            "metadata": STATSCAN_METADATA_COLLECTION,
            "logs": STATSCAN_UPDATE_LOGS_COLLECTION
        }
    }

    if source not in collections:
        raise ValueError(f"Unknown data source: {source}. Must be one of: {list(collections.keys())}")

    return collections[source]


def get_storage_prefix(source: str) -> str:
    """
    Get Cloud Storage path prefix for a data source.

    Args:
        source: Data source identifier ("fred", "yfinance", "statscan")

    Returns:
        str: Storage path prefix

    Raises:
        ValueError: If source is not recognized
    """
    prefixes = {
        "fred": FRED_STORAGE_PREFIX,
        "yfinance": YFINANCE_STORAGE_PREFIX,
        "statscan": STATSCAN_STORAGE_PREFIX
    }

    if source not in prefixes:
        raise ValueError(f"Unknown data source: {source}. Must be one of: {list(prefixes.keys())}")

    return prefixes[source]


def get_freshness_threshold(source: str, frequency: str) -> int:
    """
    Get cache freshness threshold in hours for a given source and frequency.

    Args:
        source: Data source identifier ("fred", "yfinance", "statscan")
        frequency: Data frequency (e.g., "daily", "monthly", "1d", etc.)

    Returns:
        int: Freshness threshold in hours

    Raises:
        ValueError: If source or frequency is not recognized
    """
    if source not in FRESHNESS_THRESHOLDS:
        raise ValueError(f"Unknown data source: {source}")

    if frequency not in FRESHNESS_THRESHOLDS[source]:
        # Default to daily if frequency not found
        return FRESHNESS_THRESHOLDS[source].get("daily", 24)

    return FRESHNESS_THRESHOLDS[source][frequency]
