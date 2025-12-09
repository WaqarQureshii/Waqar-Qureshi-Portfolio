"""
Authorization and permissions module for portfolio webapp.

This module handles admin detection, role management, and user queries.
Admin privileges are granted based on email match with configured admin_email.

Admin email: waqar.qureshi.uoft@gmail.com (configured in secrets.toml)
"""

from typing import Dict, List, Any
from datetime import datetime

import streamlit as st

from src.config.settings import get_app_config
from src.services.firebase_service import FirebaseService


def is_admin(email: str = None) -> bool:
    """
    Check if user has admin privileges.

    Admin status is determined by email match with st.secrets["app"]["admin_email"].
    Result is cached in st.session_state["is_admin"] for performance.

    Args:
        email: Email to check. If None, uses st.user.email

    Returns:
        bool: True if user is admin

    Admin email: waqar.qureshi.uoft@gmail.com
    """
    # If email not provided, use current user's email
    if email is None:
        if not st.user.is_logged_in:
            return False
        email = st.user.email

    # Get admin email from config
    try:
        app_config = get_app_config()
        admin_email = app_config["admin_email"]
    except KeyError:
        st.error("Admin configuration not found in secrets.toml")
        return False

    # Case-insensitive comparison
    return email.lower() == admin_email.lower()


def get_user_role(email: str = None) -> str:
    """
    Get user's role string for display purposes.

    Args:
        email: Email to check. If None, uses st.user.email

    Returns:
        str: "Admin" or "User" based on is_admin() check
    """
    return "Admin" if is_admin(email) else "User"


def require_admin(feature_name: str = "This feature") -> bool:
    """
    Guard function for admin-only features.

    Shows error message if current user is not admin.

    Args:
        feature_name: Name of the feature requiring admin access (for display)

    Returns:
        bool: True if user is admin, False otherwise

    Usage:
        if not require_admin("User Management"):
            st.stop()
    """
    if not st.user.is_logged_in:
        st.error(f"{feature_name} requires admin access. Please log in.")
        return False

    if not is_admin():
        st.error(f"{feature_name} is only available to administrators.")
        return False

    return True


def get_all_users() -> List[Dict[str, Any]]:
    """
    Fetch all registered users from Firestore (admin-only).

    Returns list of user dicts sorted by last_login (most recent first).

    Returns:
        list[dict]: List of user dicts with keys:
            - email: str
            - name: str
            - picture: str
            - last_login: datetime
            - first_login: datetime
            - login_count: int

    Raises:
        PermissionError: If current user is not admin

    Note: Timestamps are converted from Firestore timestamps to Python datetime objects.
    """
    # Check admin permission
    if not is_admin():
        raise PermissionError("Only administrators can view user list")

    try:
        # Get Firebase service
        firebase_service = FirebaseService()
        db = firebase_service.db

        # Query all users
        users_ref = db.collection("users")
        users_docs = users_ref.stream()

        users_list = []
        for doc in users_docs:
            user_data = doc.to_dict()

            # Convert Firestore timestamps to datetime
            last_login = user_data.get("last_login")
            first_login = user_data.get("first_login")

            # Handle both Firestore timestamp objects and datetime objects
            if hasattr(last_login, "timestamp"):
                last_login = datetime.fromtimestamp(last_login.timestamp())
            if hasattr(first_login, "timestamp"):
                first_login = datetime.fromtimestamp(first_login.timestamp())

            users_list.append({
                "email": user_data.get("email", ""),
                "name": user_data.get("name", ""),
                "picture": user_data.get("picture", ""),
                "sub": user_data.get("sub", ""),
                "last_login": last_login,
                "first_login": first_login,
                "login_count": user_data.get("login_count", 0)
            })

        # Sort by last_login (most recent first)
        users_list.sort(key=lambda x: x["last_login"] if x["last_login"] else datetime.min, reverse=True)

        return users_list

    except Exception as e:
        st.error(f"Failed to fetch users: {str(e)}")
        return []


def get_user_login_info(email: str) -> Dict[str, Any]:
    """
    Get login information for a specific user (admin-only).

    Args:
        email: User email to lookup

    Returns:
        dict: User login info with same structure as get_all_users()
        Empty dict if user not found

    Raises:
        PermissionError: If current user is not admin
    """
    # Check admin permission
    if not is_admin():
        raise PermissionError("Only administrators can view user information")

    try:
        # Get Firebase service
        firebase_service = FirebaseService()
        db = firebase_service.db

        # Sanitize email for document ID
        doc_id = email.replace(".", "_").replace("@", "_at_")

        # Get user document
        user_ref = db.collection("users").document(doc_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return {}

        user_data = user_doc.to_dict()

        # Convert timestamps
        last_login = user_data.get("last_login")
        first_login = user_data.get("first_login")

        if hasattr(last_login, "timestamp"):
            last_login = datetime.fromtimestamp(last_login.timestamp())
        if hasattr(first_login, "timestamp"):
            first_login = datetime.fromtimestamp(first_login.timestamp())

        return {
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "picture": user_data.get("picture", ""),
            "sub": user_data.get("sub", ""),
            "last_login": last_login,
            "first_login": first_login,
            "login_count": user_data.get("login_count", 0)
        }

    except Exception as e:
        st.error(f"Failed to fetch user info: {str(e)}")
        return {}
