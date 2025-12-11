"""
Yahoo Finance API integration using yfinance library.

Fetches historical equity market data and converts to Polars DataFrames
for consistency with other data sources in the portfolio webapp.
"""

import yfinance as yf
import polars as pl
import pandas as pd
import time
from typing import Dict, Any, Optional


class YFinanceService:
    """
    Service for fetching equity market data from Yahoo Finance.

    Uses yfinance library to fetch historical price data and converts to
    Polars DataFrames for consistency with the project.

    No API key required for yfinance.

    Attributes:
        RATE_LIMIT_DELAY: Delay between requests in seconds (conservative)

    Example:
        >>> yf_service = YFinanceService()
        >>> data = yf_service.get_ticker_history("AAPL", period="1y", interval="1d")
        >>> print(data.head())
    """

    RATE_LIMIT_DELAY = 0.1  # Conservative rate limiting (no official limit)

    def __init__(self):
        """
        Initialize yfinance service.

        No credentials needed for yfinance.
        """
        pass

    def get_ticker_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pl.DataFrame:
        """
        Fetch historical price data for a ticker.

        Args:
            ticker: Ticker symbol (e.g., "AAPL", "^GSPC", "^VIX")
                   Special characters like ^ are supported natively
            period: Time period to fetch. Valid values:
                   "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
            interval: Data interval. Valid values:
                     "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"

        Returns:
            Polars DataFrame with columns: ["date", "open", "high", "low", "close", "volume"]
            - date: Date type
            - open/high/low/close: Float64
            - volume: Int64

        Raises:
            ValueError: If ticker not found or data fetch fails

        Example:
            >>> yf_service = YFinanceService()
            >>> # Fetch Apple stock data for 1 year
            >>> data = yf_service.get_ticker_history("AAPL", period="1y", interval="1d")
            >>> print(f"Rows: {len(data)}, Columns: {data.columns}")
            >>>
            >>> # Fetch S&P 500 index (special character ticker)
            >>> sp500 = yf_service.get_ticker_history("^GSPC", period="6mo")
        """
        try:
            # Create ticker object
            ticker_obj = yf.Ticker(ticker)

            # Fetch historical data
            hist = ticker_obj.history(period=period, interval=interval)

            # Check if data is empty
            if hist.empty:
                raise ValueError(
                    f"No data available for ticker '{ticker}'. "
                    f"Verify the ticker symbol is correct and data exists for the specified period."
                )

            # Convert to Polars DataFrame
            df_polars = self._convert_history_to_dataframe(hist, ticker)

            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

            return df_polars

        except ValueError:
            # Re-raise ValueError as-is (already has good context)
            raise
        except Exception as e:
            error_str = str(e).lower()

            # Check for common error patterns
            if "404" in error_str or "not found" in error_str:
                raise ValueError(
                    f"Ticker '{ticker}' not found. "
                    f"Check the ticker symbol spelling and ensure it exists on Yahoo Finance."
                )
            elif "no data" in error_str:
                raise ValueError(
                    f"No data available for ticker '{ticker}' with period='{period}' and interval='{interval}'. "
                    f"Try a different time period or interval."
                )
            else:
                raise ValueError(f"Failed to fetch data for ticker '{ticker}': {e}")

    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch metadata for a ticker (company name, sector, etc.).

        Args:
            ticker: Ticker symbol

        Returns:
            Dictionary containing:
                - ticker: Ticker symbol
                - longName: Company/index full name
                - shortName: Company/index short name
                - sector: Sector (if applicable, None for indices)
                - industry: Industry (if applicable, None for indices)
                - currency: Trading currency
                - exchange: Exchange name
                - quoteType: Type (EQUITY, INDEX, etc.)

        Raises:
            ValueError: If ticker not found or metadata fetch fails

        Example:
            >>> yf_service = YFinanceService()
            >>> info = yf_service.get_ticker_info("AAPL")
            >>> print(info["longName"])  # "Apple Inc."
            >>> print(info["sector"])    # "Technology"
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # Check if ticker exists (empty info dict usually means ticker not found)
            if not info or "symbol" not in info:
                raise ValueError(
                    f"Ticker '{ticker}' not found or has no available metadata. "
                    f"Verify the ticker symbol is correct."
                )

            # Extract relevant metadata
            metadata = {
                "ticker": ticker,
                "longName": info.get("longName"),
                "shortName": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "currency": info.get("currency"),
                "exchange": info.get("exchange"),
                "quoteType": info.get("quoteType")
            }

            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

            return metadata

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to fetch metadata for ticker '{ticker}': {e}")

    def _convert_history_to_dataframe(
        self,
        hist: pd.DataFrame,
        ticker: str
    ) -> pl.DataFrame:
        """
        Convert yfinance history DataFrame to Polars DataFrame.

        Standardizes the DataFrame format:
        1. Reset index to get dates as column
        2. Lowercase column names
        3. Select only required columns
        4. Convert to Polars
        5. Cast date to pl.Date type
        6. Sort by date

        Args:
            hist: pandas DataFrame from yfinance (DatetimeIndex + OHLCV columns)
            ticker: Ticker symbol (for error messages)

        Returns:
            Polars DataFrame with columns: ["date", "open", "high", "low", "close", "volume"]

        Raises:
            ValueError: If conversion fails
        """
        try:
            # Reset index to get dates as a column
            df_pandas = hist.reset_index()

            # Standardize column names to lowercase
            df_pandas.columns = [col.lower() for col in df_pandas.columns]

            # Handle different possible date column names
            date_col = None
            for possible_name in ["date", "datetime", "timestamp"]:
                if possible_name in df_pandas.columns:
                    date_col = possible_name
                    break

            if date_col is None:
                raise ValueError(f"Could not find date column in data for ticker '{ticker}'")

            # Rename to standard "date"
            if date_col != "date":
                df_pandas = df_pandas.rename(columns={date_col: "date"})

            # Select only required columns (ignore others like dividends, stock splits)
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            available_cols = [col for col in required_cols if col in df_pandas.columns]

            if "date" not in available_cols or "close" not in available_cols:
                raise ValueError(
                    f"Missing required columns (date, close) in data for ticker '{ticker}'"
                )

            df_pandas = df_pandas[available_cols]

            # Convert to Polars
            df_polars = pl.from_pandas(df_pandas)

            # Ensure date column is Date type (convert from datetime if needed)
            df_polars = df_polars.with_columns([
                pl.col("date").cast(pl.Date).alias("date")
            ])

            # Sort by date (ascending)
            df_polars = df_polars.sort("date")

            return df_polars

        except Exception as e:
            raise ValueError(f"Failed to convert history data for ticker '{ticker}': {e}")
