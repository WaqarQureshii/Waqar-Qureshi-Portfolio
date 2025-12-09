"""
Google OAuth authentication module for portfolio webapp.

This module provides core authentication logic using Streamlit's native OIDC support.
All user login events are automatically logged to Firestore for admin tracking.

CRITICAL: Uses st.login() and st.logout() from Streamlit 1.42+.
"""

import time
from typing import Dict, Any
from datetime import datetime

import streamlit as st
from google.cloud import firestore

from src.services.firebase_service import FirebaseService


def initialize_auth_state() -> None:
    """
    Initialize authentication state on app load.

    This function should be called at the top of Home.py and all pages
    to ensure auth state is properly initialized.

    Actions:
    - Check if user is logged in via st.user.is_logged_in
    - Validate token expiration
    - Cache admin status in st.session_state
    - Re-initialize session state after browser refresh
    - Log user login to Firestore (if newly logged in)

    Note: This function is idempotent and safe to call multiple times.
    """
    # Check if token is expired
    if st.user.is_logged_in:
        check_token_expiration()

        # Cache admin status in session state
        if "is_admin" not in st.session_state:
            from src.auth.permissions import is_admin
            st.session_state["is_admin"] = is_admin()

        # Log user login if this is a new session
        # Use a session flag to avoid logging on every page refresh
        if "login_logged" not in st.session_state:
            try:
                log_user_login()
                st.session_state["login_logged"] = True
            except Exception as e:
                # Don't block user experience if logging fails
                st.warning(f"Note: Login tracking unavailable: {str(e)}")


def check_token_expiration() -> bool:
    """
    Validate if current user's token is still valid.

    Checks st.user.exp against current timestamp and logs out user
    if token has expired.

    Returns:
        bool: True if token is valid, False if expired

    Side effects:
        - If expired: logs out user, shows warning, and triggers rerun
    """
    if not st.user.is_logged_in:
        return False

    current_time = time.time()

    # Check if token is expired
    if st.user.exp < current_time:
        st.warning("Your session has expired. Please log in again.")
        st.logout()
        st.rerun()
        return False

    # Optionally warn if token is expiring soon (within 5 minutes)
    time_remaining = st.user.exp - current_time
    if time_remaining < 300:  # 5 minutes
        st.info(f"Your session will expire in {int(time_remaining / 60)} minutes.")

    return True


def get_user_info() -> Dict[str, Any]:
    """
    Get current user information from st.user.

    Returns:
        dict: User info with keys: email, name, picture, sub
        Empty dict if not logged in

    Safety: Always check st.user.is_logged_in before calling this function.
    """
    if not st.user.is_logged_in:
        return {}

    return {
        "email": st.user.email,
        "name": st.user.name,
        "picture": getattr(st.user, "picture", None),
        "sub": st.user.sub
    }


def log_user_login() -> None:
    """
    Log user login event to Firestore.

    Creates or updates a document in the 'users' collection with:
    - email, name, picture, sub (user identifiers)
    - last_login: timestamp of current login
    - first_login: timestamp of first login (set once)
    - login_count: total number of logins

    This function is called automatically by initialize_auth_state() on login.

    Firestore Structure:
        users/ (collection)
          └─ {user_email}/ (document)
              ├─ email: str
              ├─ name: str
              ├─ picture: str
              ├─ sub: str (Google user ID)
              ├─ last_login: timestamp
              ├─ first_login: timestamp
              └─ login_count: int

    Raises:
        Exception: If Firestore connection fails (caught by caller)
    """
    if not st.user.is_logged_in:
        return

    try:
        # Get Firebase service
        firebase_service = FirebaseService()
        db = firebase_service.db

        # Use email as document ID (sanitize for Firestore path)
        user_email = st.user.email
        doc_id = user_email.replace(".", "_").replace("@", "_at_")

        # Reference to user document
        user_ref = db.collection("users").document(doc_id)

        # Get existing document
        user_doc = user_ref.get()

        now = firestore.SERVER_TIMESTAMP

        if user_doc.exists:
            # Update existing user
            user_data = user_doc.to_dict()
            user_ref.update({
                "email": user_email,
                "name": st.user.name,
                "picture": getattr(st.user, "picture", ""),
                "sub": st.user.sub,
                "last_login": now,
                "login_count": firestore.Increment(1)
            })
        else:
            # Create new user document
            user_ref.set({
                "email": user_email,
                "name": st.user.name,
                "picture": getattr(st.user, "picture", ""),
                "sub": st.user.sub,
                "first_login": now,
                "last_login": now,
                "login_count": 1
            })

    except Exception as e:
        # Log error but don't block user experience
        raise Exception(f"Failed to log user login: {str(e)}")


def require_auth(page_name: str = "This page") -> bool:
    """
    Guard function for pages requiring authentication.

    Shows login prompt if not authenticated.

    Args:
        page_name: Name of the page/feature requiring auth (for display)

    Returns:
        bool: True if authenticated, False otherwise

    Usage:
        if not require_auth("Analysis Page"):
            st.stop()

    Note: May not be used in Phase 2 (all pages currently public).
    Implemented for future use in Phase 10 admin features.
    """
    if not st.user.is_logged_in:
        st.warning(f"{page_name} requires authentication.")
        st.info("Please log in using the sidebar to access this page.")
        return False

    return True
