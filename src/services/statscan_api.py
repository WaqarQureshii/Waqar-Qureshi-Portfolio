"""
Statistics Canada Web Data Service API integration.

Based on StatsCan WDS User Guide. Refactored from archived implementation
to follow the project's service pattern with Polars DataFrame outputs.
"""

import requests
import polars as pl
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, date


class StatsCanService:
    """
    Service for Statistics Canada Web Data Service API.

    Fetches Canadian economic data from Stats Canada's public API and
    converts to Polars DataFrames for consistency with the project.

    No API key required (public API).

    Key endpoints:
    - getChangedCubeList: Check which tables have been updated
    - getCubeMetadata: Get table structure and metadata
    - getDataFromVectorsAndLatestNPeriods: Get recent data points
    - getFullTableDownloadCSV: Get complete table as CSV

    Attributes:
        BASE_URL: Stats Canada API base URL
        RATE_LIMIT_DELAY: Delay between requests (seconds)

    Example:
        >>> sc_service = StatsCanService()
        >>> data = sc_service.get_table_data("36100434", latest_n_periods=12)
        >>> print(data.head())
    """

    BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
    RATE_LIMIT_DELAY = 0.05  # 20 requests/sec max

    def __init__(self):
        """
        Initialize Stats Canada API client.

        Sets up requests session with appropriate headers.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Portfolio-Webapp/2.0',
            'Accept': 'application/json'
        })

    # =========================================================================
    # MAIN DATA FETCH METHOD (Returns Polars DataFrame)
    # =========================================================================

    def get_table_data(
        self,
        product_id: str,
        latest_n_periods: int = 12,
        vectors: Optional[List[int]] = None
    ) -> pl.DataFrame:
        """
        Fetch Stats Canada table data and return as Polars DataFrame.

        This is the main method for fetching table data. It retrieves vector
        data and converts to wide-format DataFrame.

        Args:
            product_id: 8-digit Product ID (e.g., "36100434")
            latest_n_periods: Number of recent periods to retrieve (default: 12)
            vectors: Specific vector IDs to fetch. REQUIRED for Stats Canada API.
                    Vector IDs can be found on the Stats Canada website or in
                    dataset configurations (statscan_datasets.py).

        Returns:
            Polars DataFrame with columns: ["date", "v42076", "v42077", ...]
            - Wide format with each vector as a column
            - Column naming: "v{vector_id}" (e.g., "v42076")
            - Date column is pl.Date type

        Raises:
            ValueError: If vectors not provided, table not found, or data fetch fails

        Example:
            >>> sc_service = StatsCanService()
            >>> # Fetch GDP table with specific vectors
            >>> vectors = [41690973, 41691182]  # All industries vectors
            >>> gdp_data = sc_service.get_table_data(
            ...     "36100434",
            ...     latest_n_periods=12,
            ...     vectors=vectors
            ... )
            >>> print(f"Shape: {gdp_data.shape}")
            >>> print(f"Columns: {gdp_data.columns}")
        """
        try:
            # Vectors are REQUIRED for Stats Canada API
            # Stats Canada metadata doesn't provide vector IDs - users must specify them
            if vectors is None or len(vectors) == 0:
                raise ValueError(
                    f"Vector IDs are required for Stats Canada product '{product_id}'. "
                    f"Stats Canada metadata doesn't include vector IDs. "
                    f"Find vector IDs on the Stats Canada website or use default_vectors "
                    f"from statscan_datasets.py configurations."
                )

            # Fetch data for vectors
            vector_data_list = self.get_data_from_vectors_latest_n_periods(
                vector_ids=vectors,
                latest_n=latest_n_periods
            )

            if not vector_data_list:
                raise ValueError(
                    f"No data returned for product ID '{product_id}'. "
                    f"Table may not have data for the requested period."
                )

            # Convert to Polars DataFrame
            df_polars = self._convert_vectors_to_dataframe(vector_data_list, product_id)

            return df_polars

        except ValueError:
            # Re-raise ValueError with context already added
            raise
        except Exception as e:
            raise ValueError(f"Failed to fetch table data for product ID '{product_id}': {e}")

    def _convert_vectors_to_dataframe(
        self,
        vector_data_list: List[Dict],
        product_id: str
    ) -> pl.DataFrame:
        """
        Convert Stats Canada vector data to wide-format Polars DataFrame.

        Transformation:
        - Input: List of vector objects with vectorDataPoint arrays
        - Output: Wide DataFrame with date column + vector columns
        - Column naming: "v{vector_id}" (e.g., "v42076")

        Args:
            vector_data_list: List of vector objects from API
            product_id: Product ID (for error messages)

        Returns:
            Polars DataFrame in wide format

        Raises:
            ValueError: If conversion fails

        Example transformation:
            INPUT:
            [
                {
                    "vectorId": 42076,
                    "vectorDataPoint": [
                        {"refPer": "2024-01", "value": "150.5"},
                        {"refPer": "2024-02", "value": "151.2"}
                    ]
                },
                {"vectorId": 42077, "vectorDataPoint": [...]}
            ]

            OUTPUT DataFrame:
            | date       | v42076 | v42077 |
            |------------|--------|--------|
            | 2024-01-01 | 150.5  | 205.3  |
            | 2024-02-01 | 151.2  | 206.1  |
        """
        try:
            # Build dictionary of {date: {vector_id: value}}
            data_by_date = {}

            for vector_obj in vector_data_list:
                vector_id = vector_obj.get("vectorId")
                if not vector_id:
                    continue

                data_points = vector_obj.get("vectorDataPoint", [])

                for point in data_points:
                    ref_per = point.get("refPer")
                    value = point.get("value")

                    if ref_per and value:
                        # Parse reference period to date
                        parsed_date = self._parse_ref_period(ref_per)

                        # Initialize date entry if needed
                        if parsed_date not in data_by_date:
                            data_by_date[parsed_date] = {}

                        # Store value for this vector
                        # Convert to float, handle null values
                        try:
                            data_by_date[parsed_date][f"v{vector_id}"] = float(value)
                        except (ValueError, TypeError):
                            # If value is null or not numeric, store None
                            data_by_date[parsed_date][f"v{vector_id}"] = None

            if not data_by_date:
                raise ValueError(
                    f"No valid data points found for product ID '{product_id}'. "
                    f"Check if the table has recent data."
                )

            # Convert to list of rows
            rows = []
            for date_val, vector_values in data_by_date.items():
                row = {"date": date_val}
                row.update(vector_values)
                rows.append(row)

            # Create Polars DataFrame
            df_polars = pl.DataFrame(rows)

            # Ensure date column is Date type
            df_polars = df_polars.with_columns([
                pl.col("date").cast(pl.Date).alias("date")
            ])

            # Sort by date (ascending)
            df_polars = df_polars.sort("date")

            return df_polars

        except Exception as e:
            raise ValueError(
                f"Failed to convert vector data to DataFrame for product ID '{product_id}': {e}"
            )

    def _parse_ref_period(self, ref_per: str) -> date:
        """
        Parse Stats Canada reference period to date.

        Stats Canada uses different formats depending on frequency:
        - Full date: "2024-11-01" → 2024-11-01
        - Monthly: "2024-01" → 2024-01-01
        - Quarterly: "2024-Q1" → 2024-01-01 (first month of quarter)
        - Annual: "2024" → 2024-01-01

        Args:
            ref_per: Reference period string from API

        Returns:
            date object

        Raises:
            ValueError: If format is unrecognized
        """
        try:
            if "Q" in ref_per:
                # Quarterly format: "2024-Q1"
                year, quarter = ref_per.split("-Q")
                quarter_num = int(quarter)
                # Convert quarter to first month of that quarter
                month = (quarter_num - 1) * 3 + 1
                return date(int(year), month, 1)

            elif "-" in ref_per:
                # Check if it's a full date (YYYY-MM-DD) or just year-month (YYYY-MM)
                parts = ref_per.split("-")
                if len(parts) == 3:
                    # Full date format: "2024-11-01"
                    return datetime.strptime(ref_per, "%Y-%m-%d").date()
                elif len(parts) == 2:
                    # Monthly format: "2024-01"
                    return datetime.strptime(ref_per, "%Y-%m").date()
                else:
                    raise ValueError(f"Unexpected date format with dashes: {ref_per}")

            else:
                # Annual format: "2024"
                return date(int(ref_per), 1, 1)

        except Exception as e:
            raise ValueError(f"Could not parse reference period '{ref_per}': {e}")

    # =========================================================================
    # UTILITY METHODS (Return dicts/lists, unchanged from archived code)
    # =========================================================================

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Any] = None
    ) -> Dict:
        """
        Make API request with error handling and rate limiting.

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET or POST)
            data: Request body for POST requests

        Returns:
            JSON response as dictionary

        Raises:
            Exception: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            else:  # POST
                response = self.session.post(url, json=data, timeout=30)

            response.raise_for_status()

            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

            return response.json()

        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout for {endpoint}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 409:
                raise Exception(f"Table locked (currently updating): {endpoint}")
            raise Exception(f"HTTP error {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_changed_cubes_list(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get list of tables that changed on a specific date.

        Args:
            date: ISO date string (YYYY-MM-DD). If None, uses today.

        Returns:
            List of changed tables with productId and releaseTime

        Example:
            >>> api.get_changed_cubes_list("2024-01-15")
            [{"productId": 36100434, "releaseTime": "2024-01-15T08:30"}, ...]
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        endpoint = f"getChangedCubeList/{date}"
        response = self._make_request(endpoint, method="GET")

        if response.get("status") == "SUCCESS":
            return response.get("object", [])
        return []

    def get_changed_series_list(self) -> List[Dict]:
        """
        Get list of all series that changed today.

        Returns:
            List of changed series with vectorId, productId, coordinate
        """
        endpoint = "getChangedSeriesList"
        response = self._make_request(endpoint, method="GET")

        if response.get("status") == "SUCCESS":
            object_data = response.get("object", {})
            return object_data.get("object", [])
        return []

    def get_cube_metadata(self, product_id: str) -> Optional[Dict]:
        """
        Get comprehensive metadata for a table/cube.

        Args:
            product_id: 8-digit Product ID (e.g., "36100434")

        Returns:
            Metadata including dimensions, members, title, date ranges, etc.
            Returns None if table not found.

        Example:
            >>> metadata = api.get_cube_metadata("36100434")
            >>> print(metadata["cubeTitleEn"])
            >>> print(metadata["dimension"])
        """
        endpoint = "getCubeMetadata"
        data = [{"productId": int(product_id)}]

        try:
            response = self._make_request(endpoint, method="POST", data=data)

            if isinstance(response, list) and len(response) > 0:
                result = response[0]
                if result.get("status") == "SUCCESS":
                    return result.get("object", {})
        except Exception:
            pass

        return None

    def get_series_info_from_vector(self, vector_id: int) -> Optional[Dict]:
        """
        Get metadata for a specific data series using vector ID.

        Args:
            vector_id: Vector identifier

        Returns:
            Series information including title, frequency, decimals, etc.
        """
        endpoint = "getSeriesInfoFromVector"
        data = [{"vectorId": vector_id}]

        try:
            response = self._make_request(endpoint, method="POST", data=data)

            if isinstance(response, list) and len(response) > 0:
                result = response[0]
                if result.get("status") == "SUCCESS":
                    return result.get("object", {})
        except Exception:
            pass

        return None

    def get_data_from_vectors_latest_n_periods(
        self,
        vector_ids: List[int],
        latest_n: int
    ) -> List[Dict]:
        """
        Get last N periods of data for specified vectors.

        Args:
            vector_ids: List of vector IDs
            latest_n: Number of recent periods to retrieve

        Returns:
            List of data objects with vectorDataPoint arrays

        Example:
            >>> data = api.get_data_from_vectors_latest_n_periods([42076, 42077], 12)
            >>> for series in data:
            ...     for point in series["vectorDataPoint"]:
            ...         print(point["refPer"], point["value"])
        """
        endpoint = "getDataFromVectorsAndLatestNPeriods"

        # Build request body for each vector
        data = [{"vectorId": vid, "latestN": latest_n} for vid in vector_ids]

        try:
            response = self._make_request(endpoint, method="POST", data=data)

            results = []
            if isinstance(response, list):
                for item in response:
                    if item.get("status") == "SUCCESS":
                        results.append(item.get("object", {}))

            return results
        except Exception:
            return []

    def get_bulk_vector_data_by_range(
        self,
        vector_ids: List[int],
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        Get data for vectors within a date range.

        Args:
            vector_ids: List of vector IDs
            start_date: Start date (YYYY-MM-DDTHH:MM)
            end_date: End date (YYYY-MM-DDTHH:MM)

        Returns:
            List of data objects with all data points in range
        """
        endpoint = "getBulkVectorDataByRange"
        data = {
            "vectorIds": [str(vid) for vid in vector_ids],
            "startDataPointReleaseDate": start_date,
            "endDataPointReleaseDate": end_date
        }

        try:
            response = self._make_request(endpoint, method="POST", data=data)

            results = []
            if isinstance(response, list):
                for item in response:
                    if item.get("status") == "SUCCESS":
                        results.append(item.get("object", {}))

            return results
        except Exception:
            return []

    def get_full_table_download_csv(
        self,
        product_id: str,
        language: str = "en"
    ) -> Optional[str]:
        """
        Get download URL for complete table in CSV format.

        Args:
            product_id: 8-digit Product ID
            language: "en" or "fr"

        Returns:
            Download URL string or None if failed

        Example:
            >>> url = api.get_full_table_download_csv("36100434", "en")
            >>> # Download the CSV from this URL
        """
        endpoint = f"getFullTableDownloadCSV/{product_id}/{language}"

        try:
            response = self._make_request(endpoint, method="GET")

            if response.get("status") == "SUCCESS":
                return response.get("object")
        except Exception:
            pass

        return None

    def get_full_table_download_sdmx(self, product_id: str) -> Optional[str]:
        """
        Get download URL for complete table in SDMX format.

        Args:
            product_id: 8-digit Product ID

        Returns:
            Download URL string or None if failed
        """
        endpoint = f"getFullTableDownloadSDMX/{product_id}"

        try:
            response = self._make_request(endpoint, method="GET")

            if response.get("status") == "SUCCESS":
                return response.get("object")
        except Exception:
            pass

        return None

    def get_code_sets(self) -> Optional[Dict]:
        """
        Get code sets for interpreting scalar factors, frequencies, symbols, etc.

        Returns:
            Dictionary with scalar, frequency, symbol, status code definitions
        """
        endpoint = "getCodeSets"

        try:
            response = self._make_request(endpoint, method="GET")

            if response.get("status") == "SUCCESS":
                return response.get("object", {})
        except Exception:
            pass

        return None

    def get_all_cubes_list_lite(self) -> List[Dict]:
        """
        Get complete inventory of all available tables (lightweight version).

        Returns:
            List of all tables with basic metadata
        """
        endpoint = "getAllCubesListLite"

        try:
            response = self._make_request(endpoint, method="GET")

            if isinstance(response, list):
                return response
        except Exception:
            pass

        return []

    def check_table_updated_today(self, product_id: str) -> bool:
        """
        Check if a specific table was updated today.

        Args:
            product_id: 8-digit Product ID

        Returns:
            True if table was updated today
        """
        changed_cubes = self.get_changed_cubes_list()
        return any(
            str(cube.get("productId")) == str(product_id)
            for cube in changed_cubes
        )

    def get_table_last_release_time(self, product_id: str) -> Optional[str]:
        """
        Get the last release time for a table.

        Args:
            product_id: 8-digit Product ID

        Returns:
            Release time string (ISO format) or None
        """
        metadata = self.get_cube_metadata(product_id)
        if metadata:
            return metadata.get("releaseTime")
        return None
