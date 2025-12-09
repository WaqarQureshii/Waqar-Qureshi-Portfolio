"""
Multi-Source Firebase Service for data management.

Architecture:
- Firestore: Stores lightweight metadata (release dates, schemas, row counts, etc.)
- Cloud Storage: Stores actual data files (Parquet format)

This respects Firestore's 1MB document size limit by storing only metadata
in Firestore and large data files in Cloud Storage.

Supports multiple data sources: FRED, yfinance, Stats Canada
"""

import streamlit as st
from google.cloud import firestore, storage
from google.oauth2 import service_account
import polars as pl
from datetime import datetime
from typing import Optional, Dict, List, Any, Literal
import io

from src.config.settings import get_firebase_config
from src.config.constants import (
    get_collection_names,
    get_storage_prefix,
    KEEP_VERSIONS,
    DATA_FILE_FORMAT
)

DataSource = Literal["fred", "yfinance", "statscan"]


class FirebaseService:
    """
    Service for managing multi-source data storage in Firestore (metadata)
    and Cloud Storage (data files).

    Supports: FRED, yfinance, Stats Canada
    """

    def __init__(self):
        """Initialize Firestore and Cloud Storage clients using credentials from st.secrets."""
        try:
            # Load Firebase configuration from secrets
            config = get_firebase_config()

            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                config["credentials"]
            )

            # Initialize Firestore client
            self.db = firestore.Client(
                credentials=credentials,
                project=config["project_id"]
            )

            # Initialize Cloud Storage client
            self.storage_client = storage.Client(
                credentials=credentials,
                project=config["project_id"]
            )

            # Get bucket
            self.bucket_name = config["storage_bucket"]
            self.bucket = self.storage_client.bucket(self.bucket_name)

        except Exception as e:
            raise Exception(f"Failed to initialize Firebase service: {str(e)}")

    # =========================================================================
    # METADATA OPERATIONS (Firestore)
    # =========================================================================

    def save_metadata(
        self,
        source: DataSource,
        source_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Save or update data metadata in Firestore.

        Args:
            source: Data source ("fred", "yfinance", "statscan")
            source_id: Source-specific identifier (series_id, ticker, product_id)
            metadata: Dictionary containing source-specific metadata fields
                      Must include: storage_path, row_count, columns
        """
        collections = get_collection_names(source)
        doc_ref = self.db.collection(collections["metadata"]).document(source_id)

        # Add source and timestamp
        metadata["source"] = source
        metadata["source_id"] = source_id
        metadata["last_updated"] = firestore.SERVER_TIMESTAMP

        doc_ref.set(metadata, merge=True)

    def get_metadata(
        self,
        source: DataSource,
        source_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve data metadata from Firestore.

        Args:
            source: Data source ("fred", "yfinance", "statscan")
            source_id: Source-specific identifier

        Returns:
            Metadata dictionary or None if not found
        """
        collections = get_collection_names(source)
        doc_ref = self.db.collection(collections["metadata"]).document(source_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None

    def get_all_metadata(
        self,
        source: Optional[DataSource] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata for all stored datasets.

        Args:
            source: Optional filter by data source

        Returns:
            List of metadata dictionaries
        """
        if source:
            collections = get_collection_names(source)
            docs = self.db.collection(collections["metadata"]).stream()
        else:
            # Get all sources
            all_docs = []
            for src in ["fred", "yfinance", "statscan"]:
                collections = get_collection_names(src)
                docs = self.db.collection(collections["metadata"]).stream()
                all_docs.extend([{**doc.to_dict(), "source": src} for doc in docs])
            return all_docs

        return [{**doc.to_dict()} for doc in docs]

    def delete_metadata(
        self,
        source: DataSource,
        source_id: str
    ) -> None:
        """Delete metadata from Firestore."""
        collections = get_collection_names(source)
        self.db.collection(collections["metadata"]).document(source_id).delete()

    # =========================================================================
    # DATA OPERATIONS (Cloud Storage)
    # =========================================================================

    def _generate_storage_path(
        self,
        source: DataSource,
        source_id: str,
        timestamp: Optional[str] = None
    ) -> str:
        """
        Generate storage path for a dataset.

        Args:
            source: Data source
            source_id: Source-specific identifier
            timestamp: Optional timestamp (YYYYMMDD format). If None, uses current date.
                      For yfinance, use YYYY for year-based storage.

        Returns:
            Storage path string
        """
        prefix = get_storage_prefix(source)

        if timestamp is None:
            if source == "yfinance":
                # Year-based storage for yfinance
                timestamp = datetime.now().strftime("%Y")
            else:
                # Date-based storage for FRED and Stats Canada
                timestamp = datetime.now().strftime("%Y%m%d")

        return f"{prefix}/{source_id}/{timestamp}.{DATA_FILE_FORMAT}"

    def save_data_to_storage(
        self,
        source: DataSource,
        source_id: str,
        data: pl.DataFrame,
        timestamp: Optional[str] = None
    ) -> str:
        """
        Save DataFrame to Cloud Storage.

        Args:
            source: Data source
            source_id: Source-specific identifier
            data: Polars DataFrame to store
            timestamp: Optional timestamp for versioning

        Returns:
            Storage path where file was saved
        """
        # Generate storage path
        storage_path = self._generate_storage_path(source, source_id, timestamp)

        # Convert DataFrame to Parquet bytes
        buffer = io.BytesIO()
        data.write_parquet(buffer)
        buffer.seek(0)

        # Upload to Cloud Storage
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(buffer, content_type=f"application/{DATA_FILE_FORMAT}")

        return storage_path

    def load_data_from_storage(
        self,
        storage_path: str
    ) -> Optional[pl.DataFrame]:
        """
        Load DataFrame from Cloud Storage.

        Args:
            storage_path: Path to file in Cloud Storage

        Returns:
            Polars DataFrame or None if not found
        """
        try:
            blob = self.bucket.blob(storage_path)

            if not blob.exists():
                return None

            # Download to bytes
            data_bytes = blob.download_as_bytes()
            buffer = io.BytesIO(data_bytes)

            # Read Parquet file
            return pl.read_parquet(buffer)

        except Exception as e:
            print(f"Error loading data from storage: {str(e)}")
            return None

    def delete_data_from_storage(
        self,
        storage_path: str
    ) -> None:
        """Delete data file from Cloud Storage."""
        blob = self.bucket.blob(storage_path)
        if blob.exists():
            blob.delete()

    def list_data_files(
        self,
        source: DataSource,
        source_id: Optional[str] = None
    ) -> List[str]:
        """
        List all data files in Cloud Storage for a source.

        Args:
            source: Data source
            source_id: Optional specific identifier to filter

        Returns:
            List of file paths
        """
        prefix = get_storage_prefix(source)
        if source_id:
            prefix = f"{prefix}/{source_id}/"
        else:
            prefix = f"{prefix}/"

        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    # =========================================================================
    # COMBINED OPERATIONS
    # =========================================================================

    def save_data_complete(
        self,
        source: DataSource,
        source_id: str,
        data: pl.DataFrame,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete save operation: store data in Cloud Storage and metadata in Firestore.

        Args:
            source: Data source
            source_id: Source-specific identifier
            data: Polars DataFrame
            metadata: Source-specific metadata (will be augmented with storage info)

        Returns:
            Dictionary with status and details
        """
        try:
            # Save data to Cloud Storage
            storage_path = self.save_data_to_storage(source, source_id, data)

            # Augment metadata with storage information
            metadata["storage_path"] = storage_path
            metadata["row_count"] = len(data)
            metadata["columns"] = data.columns

            # Save metadata to Firestore
            self.save_metadata(source, source_id, metadata)

            # Clean up old versions
            self.cleanup_old_versions(source, source_id, keep_latest=KEEP_VERSIONS)

            # Log the action
            self.log_update(source, source_id, "saved", {
                "row_count": len(data),
                "storage_path": storage_path
            })

            return {
                "status": "success",
                "storage_path": storage_path,
                "row_count": len(data)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def load_data_complete(
        self,
        source: DataSource,
        source_id: str,
        version: str = "latest"
    ) -> Optional[pl.DataFrame]:
        """
        Complete load operation: retrieve data using metadata.

        Args:
            source: Data source
            source_id: Source-specific identifier
            version: "latest" or specific version timestamp

        Returns:
            Polars DataFrame or None if not found
        """
        # Get metadata
        metadata = self.get_metadata(source, source_id)
        if not metadata:
            return None

        # Load data from storage path
        storage_path = metadata.get("storage_path")
        if not storage_path:
            return None

        return self.load_data_from_storage(storage_path)

    def check_data_exists(
        self,
        source: DataSource,
        source_id: str
    ) -> bool:
        """
        Check if data exists for a source and identifier.

        Args:
            source: Data source
            source_id: Source-specific identifier

        Returns:
            True if data exists in both metadata and storage
        """
        metadata = self.get_metadata(source, source_id)
        if not metadata:
            return False

        storage_path = metadata.get("storage_path")
        if not storage_path:
            return False

        blob = self.bucket.blob(storage_path)
        return blob.exists()

    # =========================================================================
    # UPDATE LOGGING
    # =========================================================================

    def log_update(
        self,
        source: DataSource,
        source_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an update action for auditing.

        Args:
            source: Data source
            source_id: Source-specific identifier
            action: "saved", "loaded", "deleted", "error", etc.
            details: Additional details about the action
        """
        collections = get_collection_names(source)
        log_ref = self.db.collection(collections["logs"]).document()

        log_entry = {
            "source": source,
            "source_id": source_id,
            "action": action,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "details": details or {}
        }

        log_ref.set(log_entry)

    def get_recent_logs(
        self,
        source: Optional[DataSource] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent update logs.

        Args:
            source: Optional filter by data source
            limit: Maximum number of logs to retrieve

        Returns:
            List of log entries
        """
        if source:
            collections = get_collection_names(source)
            logs = (
                self.db.collection(collections["logs"])
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [log.to_dict() for log in logs]
        else:
            # Get logs from all sources
            all_logs = []
            for src in ["fred", "yfinance", "statscan"]:
                collections = get_collection_names(src)
                logs = (
                    self.db.collection(collections["logs"])
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)
                    .limit(limit // 3)  # Distribute limit across sources
                    .stream()
                )
                all_logs.extend([log.to_dict() for log in logs])

            # Sort combined logs by timestamp
            all_logs.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            return all_logs[:limit]

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    def cleanup_old_versions(
        self,
        source: DataSource,
        source_id: str,
        keep_latest: int = KEEP_VERSIONS
    ) -> None:
        """
        Clean up old versions of data files, keeping only the latest N versions.

        Args:
            source: Data source
            source_id: Source-specific identifier
            keep_latest: Number of latest versions to keep
        """
        prefix = f"{get_storage_prefix(source)}/{source_id}/"
        blobs = list(self.bucket.list_blobs(prefix=prefix))

        # Sort by creation time (newest first)
        blobs.sort(key=lambda b: b.time_created, reverse=True)

        # Delete older versions
        for blob in blobs[keep_latest:]:
            blob.delete()
            print(f"Deleted old version: {blob.name}")

    def get_cache_stats(
        self,
        source: Optional[DataSource] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about cached data.

        Args:
            source: Optional filter by data source

        Returns:
            Dictionary with cache statistics
        """
        metadata_docs = self.get_all_metadata(source)

        total_datasets = len(metadata_docs)
        total_rows = sum(doc.get("row_count", 0) for doc in metadata_docs)

        # Get storage size
        if source:
            prefix = f"{get_storage_prefix(source)}/"
        else:
            prefix = ""  # All sources

        blobs = list(self.bucket.list_blobs(prefix=prefix) if prefix else self.bucket.list_blobs())
        total_size_bytes = sum(blob.size for blob in blobs if blob.name.endswith(f".{DATA_FILE_FORMAT}"))
        total_size_mb = total_size_bytes / (1024 * 1024)

        stats = {
            "total_datasets": total_datasets,
            "total_rows": total_rows,
            "total_files": len(blobs),
            "total_size_mb": round(total_size_mb, 2)
        }

        # Add per-source breakdown if looking at all sources
        if not source:
            stats["by_source"] = {}
            for src in ["fred", "yfinance", "statscan"]:
                source_docs = [d for d in metadata_docs if d.get("source") == src]
                stats["by_source"][src] = {
                    "datasets": len(source_docs),
                    "rows": sum(d.get("row_count", 0) for d in source_docs)
                }

        return stats


# =============================================================================
# CONNECTION TESTING
# =============================================================================

def test_firebase_connection() -> Dict[str, bool]:
    """
    Test Firebase/Firestore/Cloud Storage connection.

    Returns:
        Dictionary with test results
    """
    results = {
        "credentials": False,
        "firestore": False,
        "storage": False
    }

    try:
        service = FirebaseService()
        results["credentials"] = True

        # Test Firestore
        try:
            test_doc = service.db.collection("_test").document("connection_test")
            test_doc.set({"test": True, "timestamp": datetime.now()})
            test_doc.delete()
            results["firestore"] = True
        except Exception as e:
            print(f"Firestore test failed: {str(e)}")

        # Test Cloud Storage
        try:
            # List blobs (doesn't create anything)
            list(service.bucket.list_blobs(max_results=1))
            results["storage"] = True
        except Exception as e:
            print(f"Storage test failed: {str(e)}")

    except Exception as e:
        print(f"Credential test failed: {str(e)}")

    return results
