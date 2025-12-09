"""
Authentication UI components for portfolio webapp.

This module provides reusable UI components for Google OAuth authentication,
including login/logout buttons, user profile displays, and admin dashboards.
"""

from typing import List, Dict, Any

import streamlit as st
import polars as pl

from src.auth.google_auth import get_user_info
from src.auth.permissions import is_admin, get_user_role, get_all_users


def render_auth_sidebar() -> None:
    """
    Render complete authentication UI in sidebar.

    Displays different UI based on authentication status:
    - If not logged in: "Log in with Google" button
    - If logged in: User profile card with admin badge (if admin) and logout button

    This function should be called within st.sidebar context.
    """
    st.subheader("Authentication")

    if not st.user.is_logged_in:
        # Not logged in - show login button
        st.info("Log in to access personalized features")
        if st.button("🔐 Log in with Google", use_container_width=True):
            st.login(provider="google")
    else:
        # Logged in - show user profile
        render_user_profile_card()

        # Show admin badge if user is admin
        if is_admin():
            render_admin_badge()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.logout()


def render_user_profile_card() -> None:
    """
    Render compact user profile card.

    Displays:
    - Profile picture (if available, 50px circular)
    - User name (bold)
    - User email (smaller text)

    This is designed for sidebar use with clean, compact layout.
    """
    user_info = get_user_info()

    if not user_info:
        return

    # Profile picture
    if user_info.get("picture"):
        st.image(user_info["picture"], width=50)

    # User name
    st.markdown(f"**{user_info.get('name', 'User')}**")

    # User email
    st.caption(user_info.get('email', ''))


def render_admin_badge() -> None:
    """
    Render admin badge for display next to user info.

    Displays a success badge with admin indicator.
    Only renders if current user is admin.
    """
    if is_admin():
        st.success("🔑 Admin")


def render_user_list_table() -> None:
    """
    Render admin dashboard table showing all registered users.

    Admin-only component. Shows:
    - User email
    - User name
    - Last login timestamp
    - Login count

    Sorted by last login (most recent first).
    Uses Polars DataFrame with st.dataframe() for display.

    If not admin or error occurs: shows appropriate message.
    """
    try:
        # Get all users (permission check inside function)
        users = get_all_users()

        if not users:
            st.info("No users have logged in yet.")
            return

        # Convert to Polars DataFrame
        users_data = []
        for user in users:
            # Format last login timestamp
            last_login_str = ""
            if user.get("last_login"):
                last_login_str = user["last_login"].strftime("%Y-%m-%d %H:%M")

            users_data.append({
                "Email": user.get("email", ""),
                "Name": user.get("name", ""),
                "Last Login": last_login_str,
                "Login Count": user.get("login_count", 0)
            })

        # Create Polars DataFrame
        df = pl.DataFrame(users_data)

        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Last Login": st.column_config.TextColumn("Last Login", width="medium"),
                "Login Count": st.column_config.NumberColumn("Logins", width="small")
            }
        )

        # Show total count
        st.caption(f"Total users: {len(users)}")

    except PermissionError:
        st.error("This feature is only available to administrators.")
    except Exception as e:
        st.error(f"Failed to load user list: {str(e)}")


def render_login_screen(message: str = "Please log in to continue.") -> None:
    """
    Render full-page login screen for protected pages.

    Args:
        message: Custom message to display above login button

    Displays:
    - App branding/welcome message
    - Description of features requiring login
    - "Log in with Google" button
    - Privacy/security notes

    Usage:
        if not st.user.is_logged_in:
            render_login_screen("Please log in to access Analysis tools")
            st.stop()

    Note: Optional for Phase 2 - implemented for future use in Phase 10.
    """
    st.title("Welcome to Portfolio Webapp")

    st.markdown("---")

    st.info(message)

    st.markdown("""
    ### Features Available After Login:
    - Access to advanced analysis tools
    - Personalized portfolio tracking
    - Custom equity research tools
    - Admin dashboard (for administrators)

    ### Security & Privacy:
    - We use Google OAuth for secure authentication
    - Your credentials are never stored on our servers
    - We only collect basic profile information (name, email)
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Log in with Google", use_container_width=True, type="primary"):
            st.login(provider="google")

    st.markdown("---")

    st.caption("Powered by Google OAuth 2.0 | Streamlit Authentication")
