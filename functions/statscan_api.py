"""
Statistics Canada Web Data Service API integration.
Based on StatsCan WDS User Guide.
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class StatsCanAPI:
    """
    Client for Statistics Canada Web Data Service API.
    
    Key endpoints:
    - getChangedCubeList: Check which tables have been updated
    - getCubeMetadata: Get table structure and metadata
    - getDataFromVectorsAndLatestNPeriods: Get recent data points
    - getFullTableDownloadCSV: Get complete table as CSV
    """
    
    BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
    
    def __init__(self, rate_limit_delay: float = 0.05):
        """
        Initialize API client.
        
        Args:
            rate_limit_delay: Delay between requests (default 0.05s = 20 req/sec)
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Canadian-Data-Platform/1.0',
            'Accept': 'application/json'
        })
    
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
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            else:  # POST
                response = self.session.post(url, json=data, timeout=30)
            
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout for {endpoint}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 409:
                raise Exception(f"Table locked (updating): {endpoint}")
            raise Exception(f"HTTP error {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # =========================================================================
    # PRODUCT CHANGE LISTINGS
    # =========================================================================
    
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
    
    # =========================================================================
    # METADATA
    # =========================================================================
    
    def get_cube_metadata(self, product_id: str) -> Optional[Dict]:
        """
        Get comprehensive metadata for a table/cube.
        
        Args:
            product_id: 8-digit Product ID (e.g., "36100434")
            
        Returns:
            Metadata including dimensions, members, title, date ranges, etc.
            
        Example:
            >>> metadata = api.get_cube_metadata("36100434")
            >>> print(metadata["cubeTitleEn"])
            >>> print(metadata["dimension"])
        """
        endpoint = "getCubeMetadata"
        data = [{"productId": int(product_id)}]
        
        response = self._make_request(endpoint, method="POST", data=data)
        
        if isinstance(response, list) and len(response) > 0:
            result = response[0]
            if result.get("status") == "SUCCESS":
                return result.get("object", {})
        
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
        
        response = self._make_request(endpoint, method="POST", data=data)
        
        if isinstance(response, list) and len(response) > 0:
            result = response[0]
            if result.get("status") == "SUCCESS":
                return result.get("object", {})
        
        return None
    
    # =========================================================================
    # DATA ACCESS
    # =========================================================================
    
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
        
        response = self._make_request(endpoint, method="POST", data=data)
        
        results = []
        if isinstance(response, list):
            for item in response:
                if item.get("status") == "SUCCESS":
                    results.append(item.get("object", {}))
        
        return results
    
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
        
        response = self._make_request(endpoint, method="POST", data=data)
        
        results = []
        if isinstance(response, list):
            for item in response:
                if item.get("status") == "SUCCESS":
                    results.append(item.get("object", {}))
        
        return results
    
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
        
        response = self._make_request(endpoint, method="GET")
        
        if response.get("status") == "SUCCESS":
            return response.get("object")
        
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
        
        response = self._make_request(endpoint, method="GET")
        
        if response.get("status") == "SUCCESS":
            return response.get("object")
        
        return None
    
    # =========================================================================
    # SUPPLEMENTAL
    # =========================================================================
    
    def get_code_sets(self) -> Optional[Dict]:
        """
        Get code sets for interpreting scalar factors, frequencies, symbols, etc.
        
        Returns:
            Dictionary with scalar, frequency, symbol, status code definitions
        """
        endpoint = "getCodeSets"
        response = self._make_request(endpoint, method="GET")
        
        if response.get("status") == "SUCCESS":
            return response.get("object", {})
        
        return None
    
    def get_all_cubes_list_lite(self) -> List[Dict]:
        """
        Get complete inventory of all available tables (lightweight version).
        
        Returns:
            List of all tables with basic metadata
        """
        endpoint = "getAllCubesListLite"
        response = self._make_request(endpoint, method="GET")
        
        if isinstance(response, list):
            return response
        
        return []
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
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


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Initialize API client
    api = StatsCanAPI()
    
    # Example 1: Check what tables changed today
    print("=== Tables Updated Today ===")
    changed = api.get_changed_cubes_list()
    for cube in changed[:5]:  # Show first 5
        print(f"Product ID: {cube['productId']}, Release: {cube['releaseTime']}")
    
    # Example 2: Get metadata for GDP table
    print("\n=== GDP Table Metadata ===")
    metadata = api.get_cube_metadata("36100434")
    if metadata:
        print(f"Title: {metadata['cubeTitleEn']}")
        print(f"Date Range: {metadata['cubeStartDate']} to {metadata['cubeEndDate']}")
        print(f"Last Release: {metadata['releaseTime']}")
        print(f"Number of Series: {metadata['nbSeriesCube']}")
    
    # Example 3: Get recent data
    print("\n=== Recent Data Points ===")
    # Note: You'd need actual vector IDs from the metadata
    # data = api.get_data_from_vectors_latest_n_periods([42076], 3)
    # for series in data:
    #     for point in series['vectorDataPoint']:
    #         print(f"{point['refPer']}: {point['value']}")