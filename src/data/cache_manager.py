"""
Smart Cache Manager for multi-source data.

Implements get-or-fetch pattern with freshness detection:
1. Check if data exists in cache
2. Check if cached data is fresh (based on source update frequency)
3. Return cached data if fresh, otherwise fetch new data
4. Save new data to cache and return

Supports: FRED, yfinance, Stats Canada
"""

import polars as pl
from datetime import datetime, timedelta
from typing import Callable, Optional, Literal
from src.services.firebase_service import FirebaseService, DataSource
from src.config.constants import get_freshness_threshold

class CacheManager:
    """
    Manager for intelligent data caching with freshness detection.

    Uses Firebase service for storage and implements get-or-fetch pattern.
    """

    def __init__(self):
        """Initialize cache manager with Firebase service."""
        self.firebase = FirebaseService()

    def _is_data_fresh(
        self,
        metadata: dict,
        frequency: str
    ) -> bool:
        """
        Check if cached data is still fresh based on frequency.

        Args:
            metadata: Metadata from Firestore containing last_updated timestamp
            frequency: Data frequency (e.g., "daily", "monthly", "1d")

        Returns:
            True if data is fresh, False if stale
        """
        if not metadata or "last_updated" not in metadata:
            return False

        last_updated = metadata["last_updated"]

        # Handle Firestore timestamp
        if hasattr(last_updated, 'timestamp'):
            last_updated_dt = datetime.fromtimestamp(last_updated.timestamp())
        else:
            # Assume it's already a datetime
            last_updated_dt = last_updated

        # Get freshness threshold for this source and frequency
        source = metadata.get("source", "fred")
        threshold_hours = get_freshness_threshold(source, frequency)

        # Calculate age of cached data
        age = datetime.now() - last_updated_dt
        age_hours = age.total_seconds() / 3600

        return age_hours < threshold_hours

    def get_or_fetch(
        self,
        source: DataSource,
        source_id: str,
        fetch_fn: Callable[[], pl.DataFrame],
        frequency: str,
        metadata_fn: Optional[Callable[[], dict]] = None,
        force_refresh: bool = False
    ) -> pl.DataFrame:
        """
        Get data from cache or fetch if stale/missing.

        Args:
            source: Data source ("fred", "yfinance", "statscan")
            source_id: Source-specific identifier (series_id, ticker, product_id)
            fetch_fn: Function to call to fetch fresh data (returns DataFrame)
            frequency: Data frequency for freshness check
                      (e.g., "daily", "monthly", "1d", etc.)
            metadata_fn: Optional function to generate source-specific metadata
            force_refresh: If True, skip cache and always fetch fresh data

        Returns:
            Polars DataFrame with data

        Example:
            >>> cache = CacheManager()
            >>> def fetch_fred_series():
            >>>     fred = FredAPI()
            >>>     return fred.get_series("UNRATE")
            >>> def get_metadata():
            >>>     return {"units": "Percent", "frequency": "monthly"}
            >>> data = cache.get_or_fetch(
            >>>     source="fred",
            >>>     source_id="UNRATE",
            >>>     fetch_fn=fetch_fred_series,
            >>>     frequency="monthly",
            >>>     metadata_fn=get_metadata
            >>> )
        """
        # Check if cache exists and is fresh (unless force refresh)
        if not force_refresh:
            metadata = self.firebase.get_metadata(source, source_id)

            if metadata and self._is_data_fresh(metadata, frequency):
                # Cache is fresh, load and return
                print(f"[OK] Using cached data for {source}:{source_id}")
                data = self.firebase.load_data_complete(source, source_id)

                if data is not None:
                    return data
                else:
                    print(f"[WARN] Cached data missing, fetching fresh data")

        # Cache is stale, missing, or force refresh requested
        print(f"[FETCH] Fetching fresh data for {source}:{source_id}")

        try:
            # Fetch fresh data
            data = fetch_fn()

            if data is None or len(data) == 0:
                raise ValueError(f"Fetch function returned no data for {source}:{source_id}")

            # Prepare metadata
            base_metadata = {
                "frequency": frequency,
                "data_fetched_at": datetime.now().isoformat()
            }

            # Add source-specific metadata if provided
            if metadata_fn:
                additional_metadata = metadata_fn()
                base_metadata.update(additional_metadata)

            # Save to cache
            result = self.firebase.save_data_complete(
                source=source,
                source_id=source_id,
                data=data,
                metadata=base_metadata
            )

            if result["status"] == "success":
                print(f"[OK] Cached fresh data for {source}:{source_id}")
            else:
                print(f"[WARN] Failed to cache data: {result.get('error')}")

            return data

        except Exception as e:
            print(f"[ERROR] Error fetching data for {source}:{source_id}: {str(e)}")

            # Try to return stale cache as fallback
            if not force_refresh:
                metadata = self.firebase.get_metadata(source, source_id)
                if metadata:
                    print(f"  Attempting to use stale cache as fallback")
                    stale_data = self.firebase.load_data_complete(source, source_id)
                    if stale_data is not None:
                        print(f"  [WARN] Using stale data from cache")
                        return stale_data

            # No cache available, re-raise exception
            raise

    def invalidate(
        self,
        source: DataSource,
        source_id: str
    ) -> bool:
        """
        Invalidate (delete) cached data for a specific source and identifier.

        Args:
            source: Data source
            source_id: Source-specific identifier

        Returns:
            True if deleted, False if not found
        """
        if self.firebase.check_data_exists(source, source_id):
            metadata = self.firebase.get_metadata(source, source_id)
            if metadata and "storage_path" in metadata:
                # Delete data file
                self.firebase.delete_data_from_storage(metadata["storage_path"])

            # Delete metadata
            self.firebase.delete_metadata(source, source_id)

            print(f"[OK] Invalidated cache for {source}:{source_id}")
            return True
        else:
            print(f"[WARN] No cache found for {source}:{source_id}")
            return False

    def get_cache_info(
        self,
        source: DataSource,
        source_id: str
    ) -> Optional[dict]:
        """
        Get cache information for a specific dataset.

        Args:
            source: Data source
            source_id: Source-specific identifier

        Returns:
            Dictionary with cache info or None if not cached
        """
        metadata = self.firebase.get_metadata(source, source_id)

        if not metadata:
            return None

        # Calculate age
        last_updated = metadata.get("last_updated")
        if hasattr(last_updated, 'timestamp'):
            last_updated_dt = datetime.fromtimestamp(last_updated.timestamp())
        else:
            last_updated_dt = last_updated

        age = datetime.now() - last_updated_dt
        age_hours = age.total_seconds() / 3600

        frequency = metadata.get("frequency", "unknown")
        is_fresh = self._is_data_fresh(metadata, frequency)

        return {
            "source": source,
            "source_id": source_id,
            "last_updated": last_updated_dt.isoformat() if last_updated_dt else None,
            "age_hours": round(age_hours, 2),
            "is_fresh": is_fresh,
            "frequency": frequency,
            "row_count": metadata.get("row_count", 0),
            "storage_path": metadata.get("storage_path", "")
        }

    def get_all_cache_info(
        self,
        source: Optional[DataSource] = None
    ) -> list:
        """
        Get cache information for all datasets.

        Args:
            source: Optional filter by data source

        Returns:
            List of cache info dictionaries
        """
        all_metadata = self.firebase.get_all_metadata(source)

        cache_info_list = []
        for metadata in all_metadata:
            src = metadata.get("source")
            src_id = metadata.get("source_id")

            if src and src_id:
                info = self.get_cache_info(src, src_id)
                if info:
                    cache_info_list.append(info)

        return cache_info_list

    def get_stats(
        self,
        source: Optional[DataSource] = None
    ) -> dict:
        """
        Get cache statistics.

        Args:
            source: Optional filter by data source

        Returns:
            Dictionary with cache statistics
        """
        return self.firebase.get_cache_stats(source)

    def cleanup_all_old_versions(
        self,
        source: Optional[DataSource] = None
    ) -> None:
        """
        Clean up old versions for all cached datasets.

        Args:
            source: Optional filter by data source
        """
        all_metadata = self.firebase.get_all_metadata(source)

        for metadata in all_metadata:
            src = metadata.get("source")
            src_id = metadata.get("source_id")

            if src and src_id:
                print(f"Cleaning up old versions for {src}:{src_id}")
                self.firebase.cleanup_old_versions(src, src_id)

        print("[OK] Cleanup complete")
