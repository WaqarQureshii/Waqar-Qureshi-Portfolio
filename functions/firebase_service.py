"""
Google Cloud Firestore and Cloud Storage service for data management.

Architecture:
- Firestore: Stores metadata (release dates, schemas, row counts, etc.)
- Cloud Storage: Stores actual data files (Parquet format)

This respects Firestore's 1MB document size limit by only storing lightweight
metadata in Firestore and large data files in Cloud Storage.
"""

import streamlit as st
from google.cloud import firestore, storage
from google.oauth2 import service_account
import polars as pl
from datetime import datetime
from typing import Optional, Dict, List, Any
import io
import json


class FirebaseService:
    """
    Service for managing data storage in Firestore (metadata) and Cloud Storage (data files).
    """
    
    def __init__(self):
        """Initialize Firestore and Cloud Storage clients using Streamlit secrets."""
        try:
            # Get credentials from Streamlit secrets
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            
            # Initialize Firestore client
            self.db = firestore.Client(
                credentials=credentials,
                project=st.secrets["gcp_service_account"]["project_id"]
            )
            
            # Initialize Cloud Storage client
            self.storage_client = storage.Client(
                credentials=credentials,
                project=st.secrets["gcp_service_account"]["project_id"]
            )
            
            self.bucket_name = st.secrets["firebase"]["bucket_name"]
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            # Collection names
            self.metadata_collection = "table_metadata"
            self.update_log_collection = "update_logs"
            
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase service: {str(e)}")
    
    # =========================================================================
    # METADATA OPERATIONS (Firestore)
    # =========================================================================
    
    def save_table_metadata(
        self,
        product_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Save or update table metadata in Firestore.
        
        Args:
            product_id: StatsCan Product ID
            metadata: Dictionary containing:
                - release_time: Last release timestamp from API
                - title_en: English title
                - title_fr: French title
                - start_date: Data start date
                - end_date: Data end date
                - row_count: Number of rows in data
                - columns: List of column names
                - storage_path: Path to data file in Cloud Storage
                - last_updated: Timestamp of last local update
                - friendly_name: Optional friendly reference name
        """
        doc_ref = self.db.collection(self.metadata_collection).document(product_id)
        
        # Add timestamp
        metadata["last_updated"] = firestore.SERVER_TIMESTAMP
        
        doc_ref.set(metadata, merge=True)
    
    def get_table_metadata(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve table metadata from Firestore.
        
        Args:
            product_id: StatsCan Product ID
            
        Returns:
            Metadata dictionary or None if not found
        """
        doc_ref = self.db.collection(self.metadata_collection).document(product_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_all_table_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all stored tables.
        
        Returns:
            List of metadata dictionaries
        """
        docs = self.db.collection(self.metadata_collection).stream()
        return [{"product_id": doc.id, **doc.to_dict()} for doc in docs]
    
    def delete_table_metadata(self, product_id: str) -> None:
        """Delete table metadata from Firestore."""
        self.db.collection(self.metadata_collection).document(product_id).delete()
    
    # =========================================================================
    # DATA OPERATIONS (Cloud Storage)
    # =========================================================================
    
    def save_data_to_storage(
        self,
        product_id: str,
        data: pl.DataFrame,
        file_format: str = "parquet"
    ) -> str:
        """
        Save DataFrame to Cloud Storage.
        
        Args:
            product_id: StatsCan Product ID
            data: Polars DataFrame to store
            file_format: "parquet" or "csv"
            
        Returns:
            Storage path where file was saved
        """
        # Create storage path
        timestamp = datetime.now().strftime("%Y%m%d")
        file_extension = "parquet" if file_format == "parquet" else "csv"
        storage_path = f"statscan/{product_id}/{timestamp}.{file_extension}"
        
        # Convert DataFrame to bytes
        if file_format == "parquet":
            buffer = io.BytesIO()
            data.write_parquet(buffer)
            buffer.seek(0)
        else:  # CSV
            buffer = io.BytesIO(data.write_csv().encode())
            buffer.seek(0)
        
        # Upload to Cloud Storage
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(buffer, content_type=f"application/{file_extension}")
        
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
            
            # Read based on file extension
            if storage_path.endswith(".parquet"):
                return pl.read_parquet(buffer)
            elif storage_path.endswith(".csv"):
                return pl.read_csv(buffer)
            else:
                raise ValueError(f"Unsupported file format: {storage_path}")
                
        except Exception as e:
            print(f"Error loading data from storage: {str(e)}")
            return None
    
    def delete_data_from_storage(self, storage_path: str) -> None:
        """Delete data file from Cloud Storage."""
        blob = self.bucket.blob(storage_path)
        if blob.exists():
            blob.delete()
    
    def list_data_files(self, prefix: str = "statscan/") -> List[str]:
        """
        List all data files in Cloud Storage with given prefix.
        
        Args:
            prefix: Path prefix to filter files
            
        Returns:
            List of file paths
        """
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    
    # =========================================================================
    # COMBINED OPERATIONS
    # =========================================================================
    
    def save_table_complete(
        self,
        product_id: str,
        data: pl.DataFrame,
        statscan_metadata: Dict[str, Any],
        friendly_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Complete save operation: store data in Cloud Storage and metadata in Firestore.
        
        Args:
            product_id: StatsCan Product ID
            data: Polars DataFrame
            statscan_metadata: Metadata from StatsCan API
            friendly_name: Optional friendly reference name
            
        Returns:
            Dictionary with storage_path and status
        """
        try:
            # Save data to Cloud Storage
            storage_path = self.save_data_to_storage(product_id, data)
            
            # Prepare metadata for Firestore
            metadata = {
                "release_time": statscan_metadata.get("releaseTime"),
                "title_en": statscan_metadata.get("cubeTitleEn"),
                "title_fr": statscan_metadata.get("cubeTitleFr"),
                "start_date": statscan_metadata.get("cubeStartDate"),
                "end_date": statscan_metadata.get("cubeEndDate"),
                "row_count": len(data),
                "columns": data.columns,
                "storage_path": storage_path,
                "friendly_name": friendly_name
            }
            
            # Save metadata to Firestore
            self.save_table_metadata(product_id, metadata)
            
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
    
    def load_table_complete(
        self,
        product_id: str
    ) -> Optional[pl.DataFrame]:
        """
        Complete load operation: retrieve data using metadata.
        
        Args:
            product_id: StatsCan Product ID
            
        Returns:
            Polars DataFrame or None if not found
        """
        # Get metadata
        metadata = self.get_table_metadata(product_id)
        if not metadata:
            return None
        
        # Load data from storage path
        storage_path = metadata.get("storage_path")
        if not storage_path:
            return None
        
        return self.load_data_from_storage(storage_path)
    
    def check_data_exists(self, product_id: str) -> bool:
        """
        Check if data exists for a product ID.
        
        Args:
            product_id: StatsCan Product ID
            
        Returns:
            True if data exists in both metadata and storage
        """
        metadata = self.get_table_metadata(product_id)
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
        product_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an update action for auditing.
        
        Args:
            product_id: StatsCan Product ID
            action: "fetched", "updated", "error", etc.
            details: Additional details about the action
        """
        log_ref = self.db.collection(self.update_log_collection).document()
        
        log_entry = {
            "product_id": product_id,
            "action": action,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "details": details or {}
        }
        
        log_ref.set(log_entry)
    
    def get_recent_update_logs(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent update logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of log entries
        """
        logs = (
            self.db.collection(self.update_log_collection)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        
        return [log.to_dict() for log in logs]
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def clear_old_versions(
        self,
        product_id: str,
        keep_latest: int = 3
    ) -> None:
        """
        Clear old versions of data files, keeping only the latest N versions.
        
        Args:
            product_id: StatsCan Product ID
            keep_latest: Number of latest versions to keep
        """
        prefix = f"statscan/{product_id}/"
        blobs = list(self.bucket.list_blobs(prefix=prefix))
        
        # Sort by creation time (newest first)
        blobs.sort(key=lambda b: b.time_created, reverse=True)
        
        # Delete older versions
        for blob in blobs[keep_latest:]:
            blob.delete()
            print(f"Deleted old version: {blob.name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about cached data.
        
        Returns:
            Dictionary with cache statistics
        """
        metadata_docs = self.get_all_table_metadata()
        
        total_tables = len(metadata_docs)
        total_rows = sum(doc.get("row_count", 0) for doc in metadata_docs)
        
        # Get storage size
        blobs = list(self.bucket.list_blobs(prefix="statscan/"))
        total_size_bytes = sum(blob.size for blob in blobs)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        return {
            "total_tables": total_tables,
            "total_rows": total_rows,
            "total_files": len(blobs),
            "total_size_mb": round(total_size_mb, 2)
        }


# =============================================================================
# CONNECTION TESTING
# =============================================================================

def test_firebase_connection() -> Dict[str, bool]:
    """
    Test Firebase/Firestore connection.
    
    Returns:
        Dictionary with test results
    """
    results = {
        "firestore": False,
        "storage": False,
        "credentials": False
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


if __name__ == "__main__":
    # Test connection
    print("Testing Firebase connection...")
    results = test_firebase_connection()
    
    print("\nConnection Test Results:")
    print(f"  Credentials: {'✓' if results['credentials'] else '✗'}")
    print(f"  Firestore: {'✓' if results['firestore'] else '✗'}")
    print(f"  Cloud Storage: {'✓' if results['storage'] else '✗'}")
    
    if all(results.values()):
        print("\n✓ All connections successful!")
    else:
        print("\n✗ Some connections failed. Check your configuration.")