"""
FRED (Federal Reserve Economic Data) API Service.

Provides methods to fetch economic data from FRED using the fredapi library.
Returns data as Polars DataFrames for consistency with project standards.

CRITICAL: Must load API key from st.secrets["fred"]["api_key"].
"""

import time
from typing import Optional, List, Dict, Any
from fredapi import Fred
import polars as pl
import pandas as pd

from src.config.settings import get_fred_config


class FredService:
    """
    Service for fetching data from FRED API.

    Uses the fredapi library to fetch economic data and converts it to
    Polars DataFrames for consistency with the project.

    Attributes:
        fred: fredapi.Fred client instance
        RATE_LIMIT_DELAY: Delay between requests (seconds)
    """

    RATE_LIMIT_DELAY = 0.1  # 10 requests per second max

    def __init__(self):
        """
        Initialize FRED API client with API key from secrets.

        Raises:
            KeyError: If FRED API key not found in st.secrets
        """
        try:
            config = get_fred_config()
            self.fred = Fred(api_key=config["api_key"])
        except KeyError as e:
            raise KeyError(
                f"FRED API key not configured: {e}. "
                "Add [fred] api_key to .streamlit/secrets.toml"
            )

    def get_series(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None
    ) -> pl.DataFrame:
        """
        Fetch a single FRED series and return as Polars DataFrame.

        Args:
            series_id: FRED series identifier (e.g., "DGS10")
            observation_start: Start date (YYYY-MM-DD format)
            observation_end: End date (YYYY-MM-DD format)

        Returns:
            Polars DataFrame with columns: ["date", "value"]

        Raises:
            ValueError: If series not found or data fetch fails

        Example:
            >>> fred = FredService()
            >>> data = fred.get_series("DGS10")
            >>> print(data.head())
        """
        try:
            # Fetch series from FRED API
            series_data = self.fred.get_series(
                series_id,
                observation_start=observation_start,
                observation_end=observation_end
            )

            # Convert pandas Series to Polars DataFrame
            df = self._convert_series_to_dataframe(series_data, series_id)

            # Apply rate limiting
            self._rate_limit()

            return df

        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "unauthorized" in error_msg:
                raise ValueError(f"FRED API authentication failed: {e}")
            elif "not found" in error_msg or "400" in error_msg:
                raise ValueError(f"Series '{series_id}' not found in FRED database")
            else:
                raise ValueError(f"Failed to fetch series '{series_id}': {e}")

    def get_multiple_series(
        self,
        series_ids: List[str],
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None
    ) -> pl.DataFrame:
        """
        Fetch multiple FRED series and return as wide-format DataFrame.

        Args:
            series_ids: List of FRED series identifiers
            observation_start: Start date (YYYY-MM-DD format)
            observation_end: End date (YYYY-MM-DD format)

        Returns:
            Polars DataFrame with columns: ["date", series_id_1, series_id_2, ...]
            Each series becomes a column with the series_id as column name

        Raises:
            ValueError: If any series fails to fetch

        Example:
            >>> fred = FredService()
            >>> yields = fred.get_multiple_series(["DGS2", "DGS10", "DGS30"])
            >>> print(yields.head())
        """
        if not series_ids:
            raise ValueError("series_ids list cannot be empty")

        # Fetch each series
        series_dfs = {}
        for series_id in series_ids:
            try:
                series_data = self.fred.get_series(
                    series_id,
                    observation_start=observation_start,
                    observation_end=observation_end
                )

                # Convert to DataFrame with series_id as column name
                df_pandas = series_data.reset_index()
                df_pandas.columns = ["date", series_id]

                series_dfs[series_id] = df_pandas

                # Apply rate limiting
                self._rate_limit()

            except Exception as e:
                raise ValueError(f"Failed to fetch series '{series_id}': {e}")

        # Merge all series on date
        if not series_dfs:
            raise ValueError("No series data fetched")

        # Start with first series
        first_id = list(series_dfs.keys())[0]
        merged_df = series_dfs[first_id]

        # Merge remaining series
        for series_id in list(series_dfs.keys())[1:]:
            merged_df = merged_df.merge(
                series_dfs[series_id],
                on="date",
                how="outer"
            )

        # Convert to Polars
        df_polars = pl.from_pandas(merged_df)

        # Ensure date column is Date type
        df_polars = df_polars.with_columns([
            pl.col("date").cast(pl.Date).alias("date")
        ])

        # Sort by date
        df_polars = df_polars.sort("date")

        return df_polars

    def get_series_metadata(self, series_id: str) -> Dict[str, Any]:
        """
        Fetch metadata for a FRED series.

        Args:
            series_id: FRED series identifier

        Returns:
            Dictionary containing:
                - title: Series title
                - units: Units of measurement
                - frequency: Data frequency
                - seasonal_adjustment: Seasonal adjustment method
                - last_updated: API's last update timestamp
                - notes: Additional notes about the series

        Raises:
            ValueError: If series not found

        Example:
            >>> fred = FredService()
            >>> meta = fred.get_series_metadata("UNRATE")
            >>> print(meta["title"])
            "Unemployment Rate"
        """
        try:
            info = self.fred.get_series_info(series_id)

            # Extract relevant fields
            metadata = {
                "series_id": series_id,
                "title": info.get("title", ""),
                "units": info.get("units", ""),
                "frequency": info.get("frequency", ""),
                "seasonal_adjustment": info.get("seasonal_adjustment", ""),
                "last_updated": info.get("last_updated", ""),
                "notes": info.get("notes", "")
            }

            # Apply rate limiting
            self._rate_limit()

            return metadata

        except Exception as e:
            if "not found" in str(e).lower() or "400" in str(e):
                raise ValueError(f"Series '{series_id}' not found in FRED database")
            else:
                raise ValueError(f"Failed to fetch metadata for '{series_id}': {e}")

    def get_series_info_summary(self, series_id: str) -> str:
        """
        Get a human-readable summary of series information.

        Args:
            series_id: FRED series identifier

        Returns:
            Formatted string with series details
        """
        try:
            meta = self.get_series_metadata(series_id)

            summary = f"""
Series: {meta['series_id']}
Title: {meta['title']}
Units: {meta['units']}
Frequency: {meta['frequency']}
Seasonal Adjustment: {meta['seasonal_adjustment']}
Last Updated: {meta['last_updated']}
            """.strip()

            return summary

        except Exception as e:
            return f"Error fetching info for {series_id}: {e}"

    def _convert_series_to_dataframe(
        self,
        series: pd.Series,
        series_id: str
    ) -> pl.DataFrame:
        """
        Convert pandas Series to Polars DataFrame.

        Args:
            series: Pandas Series from fredapi
            series_id: Series identifier (for error messages)

        Returns:
            Polars DataFrame with columns: ["date", "value"]

        Raises:
            ValueError: If conversion fails
        """
        try:
            # Reset index to get dates as column
            df_pandas = series.reset_index()
            df_pandas.columns = ["date", "value"]

            # Convert to Polars
            df_polars = pl.from_pandas(df_pandas)

            # Ensure date column is Date type
            df_polars = df_polars.with_columns([
                pl.col("date").cast(pl.Date).alias("date")
            ])

            # Filter out null values
            df_polars = df_polars.filter(pl.col("value").is_not_null())

            return df_polars

        except Exception as e:
            raise ValueError(
                f"Failed to convert series '{series_id}' to DataFrame: {e}"
            )

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        time.sleep(self.RATE_LIMIT_DELAY)
