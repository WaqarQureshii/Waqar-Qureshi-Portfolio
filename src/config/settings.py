"""
Configuration settings loader for portfolio webapp.

CRITICAL: All credentials MUST be loaded from st.secrets.
NEVER hardcode API keys, passwords, or tokens in this file.

This module provides clean accessor functions for configuration values
stored in .streamlit/secrets.toml.
"""

import streamlit as st
from typing import Dict, Any


def get_firebase_config() -> Dict[str, Any]:
    """
    Load Firebase/GCP configuration from st.secrets.

    Returns:
        dict: Combined Firebase configuration containing:
            - credentials: GCP service account credentials
            - storage_bucket: Cloud Storage bucket name
            - project_id: Firebase project ID

    Raises:
        KeyError: If required secrets are missing
    """
    try:
        # Get GCP service account credentials
        credentials = dict(st.secrets["gcp_service_account"])

        # Get Firebase storage configuration
        storage_bucket = st.secrets["firebase"]["storage_bucket"]
        project_id = st.secrets["firebase"]["project_id"]

        return {
            "credentials": credentials,
            "storage_bucket": storage_bucket,
            "project_id": project_id
        }
    except KeyError as e:
        raise KeyError(
            f"Missing required Firebase configuration in secrets.toml: {e}. "
            "Ensure [gcp_service_account] and [firebase] sections are configured."
        )


def get_fred_config() -> Dict[str, str]:
    """
    Load FRED API configuration from st.secrets.

    Returns:
        dict: FRED configuration containing:
            - api_key: FRED API key

    Raises:
        KeyError: If FRED API key is missing
    """
    try:
        return {
            "api_key": st.secrets["fred"]["api_key"]
        }
    except KeyError as e:
        raise KeyError(
            f"Missing FRED API key in secrets.toml: {e}. "
            "Ensure [fred] section has 'api_key' configured."
        )


def get_app_config() -> Dict[str, Any]:
    """
    Load application configuration from st.secrets.

    Returns:
        dict: Application configuration containing:
            - admin_email: Email address of admin user
            - Other app-level settings

    Raises:
        KeyError: If required app configuration is missing
    """
    try:
        return {
            "admin_email": st.secrets["app"]["admin_email"]
        }
    except KeyError as e:
        raise KeyError(
            f"Missing app configuration in secrets.toml: {e}. "
            "Ensure [app] section has 'admin_email' configured."
        )


def get_auth_config() -> Dict[str, str]:
    """
    Load Google OAuth authentication configuration from st.secrets.

    Returns:
        dict: Auth configuration containing:
            - client_id: Google OAuth client ID
            - client_secret: Google OAuth client secret
            - redirect_uri: OAuth redirect URI
            - server_metadata_url: OpenID configuration URL

    Raises:
        KeyError: If required auth configuration is missing
    """
    try:
        return {
            "client_id": st.secrets["auth"]["google"]["client_id"],
            "client_secret": st.secrets["auth"]["google"]["client_secret"],
            "redirect_uri": st.secrets["auth"]["redirect_uri"],
            "server_metadata_url": st.secrets["auth"]["google"]["server_metadata_url"]
        }
    except KeyError as e:
        raise KeyError(
            f"Missing auth configuration in secrets.toml: {e}. "
            "Ensure [auth.google] and [auth] sections are configured."
        )


def verify_all_configs() -> Dict[str, bool]:
    """
    Verify that all required configurations are present in secrets.toml.

    Returns:
        dict: Status of each configuration section
            - firebase: bool
            - fred: bool
            - app: bool
            - auth: bool
    """
    status = {}

    # Check Firebase config
    try:
        get_firebase_config()
        status["firebase"] = True
    except KeyError:
        status["firebase"] = False

    # Check FRED config
    try:
        get_fred_config()
        status["fred"] = True
    except KeyError:
        status["fred"] = False

    # Check App config
    try:
        get_app_config()
        status["app"] = True
    except KeyError:
        status["app"] = False

    # Check Auth config
    try:
        get_auth_config()
        status["auth"] = True
    except KeyError:
        status["auth"] = False

    return status
