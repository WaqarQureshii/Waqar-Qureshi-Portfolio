"""
Sidebar components for data controls and status displays.

This module provides reusable sidebar widgets for:
- Date range selection
- Data source freshness indicators
- Cache refresh controls
"""

from typing import Tuple, List, Optional, Callable
from datetime import datetime, timedelta

import streamlit as st

from src.data.cache_manager import CacheManager


# =============================================================================
# DATE RANGE CONTROLS
# =============================================================================

def render_date_range_selector(
    key_prefix: str = "analysis",
    default_years_back: int = 5,
    min_date: Optional[datetime] = None,
    max_date: Optional[datetime] = None
) -> Tuple[datetime, datetime]:
    """
    Render date range selector in sidebar.

    Args:
        key_prefix: Unique prefix for session state keys
        default_years_back: Default lookback period in years
        min_date: Minimum selectable date (default: 20 years ago)
        max_date: Maximum selectable date (default: today)

    Returns:
        Tuple of (start_date, end_date)

    Example:
        >>> start_date, end_date = render_date_range_selector("chart1")
    """
    # Set defaults
    if max_date is None:
        max_date = datetime.now()

    if min_date is None:
        min_date = datetime.now() - timedelta(days=365*50)

    default_start = datetime.now() - timedelta(days=365*default_years_back)

    # Initialize session state
    if f"{key_prefix}_start_date" not in st.session_state:
        st.session_state[f"{key_prefix}_start_date"] = default_start

    if f"{key_prefix}_end_date" not in st.session_state:
        st.session_state[f"{key_prefix}_end_date"] = max_date

    # Render date inputs
    st.subheader("Date Range")

    start_date = st.date_input(
        "Start Date",
        value=st.session_state[f"{key_prefix}_start_date"],
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}_start"
    )

    end_date = st.date_input(
        "End Date",
        value=st.session_state[f"{key_prefix}_end_date"],
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}_end"
    )

    # Update session state
    st.session_state[f"{key_prefix}_start_date"] = start_date
    st.session_state[f"{key_prefix}_end_date"] = end_date

    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    return start_datetime, end_datetime


# =============================================================================
# DATA SOURCE STATUS
# =============================================================================

def render_data_source_status(
    cache_manager: CacheManager,
    sources: List[Tuple[str, str]],
    expanded: bool = False
) -> None:
    """
    Display cache freshness status for data sources.

    Args:
        cache_manager: CacheManager instance
        sources: List of (source_type, source_id) tuples
        expanded: Whether expander is expanded by default

    Example:
        >>> render_data_source_status(
        ...     cache_manager=cache,
        ...     sources=[
        ...         ("fred", "DGS10"),
        ...         ("yfinance", "^GSPC")
        ...     ]
        ... )
    """
    with st.expander("Data Source Status", expanded=expanded):
        if not sources:
            st.info("No data sources selected")
            return

        st.caption("Cache Freshness Indicators")

        for source_type, source_id in sources:
            try:
                # Get metadata from cache
                metadata = cache_manager._get_metadata(source_type, source_id)

                if metadata:
                    last_updated = metadata.get("last_updated", "Unknown")
                    row_count = metadata.get("row_count", "N/A")

                    # Format timestamp
                    if isinstance(last_updated, datetime):
                        age = datetime.now() - last_updated
                        age_str = _format_age(age)
                        status_emoji = _get_freshness_emoji(age)
                    else:
                        age_str = "Unknown"
                        status_emoji = "❓"

                    st.write(f"{status_emoji} **{source_id}** ({source_type})")
                    st.caption(f"Last updated: {age_str} | Rows: {row_count}")
                else:
                    st.write(f"⚪ **{source_id}** ({source_type})")
                    st.caption("Not cached")

            except Exception as e:
                st.write(f"❌ **{source_id}** ({source_type})")
                st.caption(f"Error: {str(e)[:50]}")

        st.divider()


def _format_age(age: timedelta) -> str:
    """Format timedelta as human-readable string."""
    days = age.days
    hours = age.seconds // 3600

    if days > 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif days > 30:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        minutes = age.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"


def _get_freshness_emoji(age: timedelta) -> str:
    """Get emoji indicator based on data age."""
    hours = age.total_seconds() / 3600

    if hours < 24:
        return "🟢"  # Fresh (< 1 day)
    elif hours < 168:
        return "🟡"  # Moderate (< 1 week)
    elif hours < 720:
        return "🟠"  # Stale (< 1 month)
    else:
        return "🔴"  # Very stale (> 1 month)


# =============================================================================
# REFRESH CONTROLS
# =============================================================================

def render_refresh_controls(
    on_refresh_callback: Optional[Callable] = None,
    button_label: str = "Force Refresh All Data",
    help_text: str = "Clear cache and fetch fresh data from all sources"
) -> bool:
    """
    Render cache refresh button with optional callback.

    Args:
        on_refresh_callback: Function to call when refresh is triggered
        button_label: Text for the refresh button
        help_text: Tooltip text for the button

    Returns:
        bool: True if refresh button was clicked

    Example:
        >>> if render_refresh_controls(on_refresh_callback=my_function):
        ...     st.success("Data refreshed!")
    """
    st.subheader("Data Management")

    refresh_clicked = st.button(
        button_label,
        help=help_text,
        type="secondary",
        use_container_width=True
    )

    if refresh_clicked:
        if on_refresh_callback:
            on_refresh_callback()
        return True

    return False


# =============================================================================
# PRESET DATE RANGES
# =============================================================================

def render_preset_date_ranges(key_prefix: str = "analysis") -> Optional[Tuple[datetime, datetime]]:
    """
    Render preset date range buttons (YTD, 1Y, 5Y, 10Y, MAX).

    Args:
        key_prefix: Unique prefix for session state keys

    Returns:
        Tuple of (start_date, end_date) if preset selected, None otherwise

    Example:
        >>> preset = render_preset_date_ranges("chart1")
        >>> if preset:
        ...     start_date, end_date = preset
    """
    st.caption("Quick Presets")

    cols = st.columns(5)

    presets = {
        "YTD": (datetime(datetime.now().year, 1, 1), datetime.now()),
        "1Y": (datetime.now() - timedelta(days=365), datetime.now()),
        "5Y": (datetime.now() - timedelta(days=365*5), datetime.now()),
        "10Y": (datetime.now() - timedelta(days=365*10), datetime.now()),
        "MAX": (datetime.now() - timedelta(days=365*20), datetime.now())
    }

    for idx, (label, (start, end)) in enumerate(presets.items()):
        with cols[idx]:
            if st.button(label, key=f"{key_prefix}_preset_{label}", use_container_width=True):
                st.session_state[f"{key_prefix}_start_date"] = start
                st.session_state[f"{key_prefix}_end_date"] = end
                return start, end

    return None
