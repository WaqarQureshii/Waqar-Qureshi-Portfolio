"""
Admin dashboard components for managing cache and monitoring system status.
"""
import streamlit as st
import polars as pl
from datetime import datetime
from typing import Dict, Any

from src.data.cache_manager import CacheManager
from src.services.fred_api import FredService
from src.services.yfinance_service import YFinanceService
# from src.services.statscan_api import StatscanService # Assuming it exists

def render_admin_dashboard(cache_manager: CacheManager, fred_service: FredService, yf_service: YFinanceService): #, statscan_service: StatscanService):
    """
    Renders the admin dashboard with cache statistics and force refresh options.
    """
    st.header("🔑 Admin Dashboard")
    st.markdown("Manage data cache and monitor service status.")

    st.subheader("Cache Management")
    st.info("Here you can view cache statistics and force a refresh of data from various sources.")

    cache_stats = cache_manager.get_cache_stats()

    if cache_stats:
        st.write("### Cache Statistics")
        st.dataframe(pl.DataFrame(cache_stats).to_pandas(), use_container_width=True) # Display as DataFrame

        st.write("### Force Data Refresh")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Refresh FRED Data", key="refresh_fred", use_container_width=True):
                with st.spinner("Refreshing FRED data..."):
                    fred_service.clear_cache() # Assuming clear_cache method exists
                    st.cache_data.clear() # Clear Streamlit's cache for relevant data
                    st.success("FRED cache cleared. Data will be re-fetched on demand.")
        with col2:
            if st.button("Refresh yfinance Data", key="refresh_yf", use_container_width=True):
                with st.spinner("Refreshing yfinance data..."):
                    yf_service.clear_cache() # Assuming clear_cache method exists
                    st.cache_data.clear() # Clear Streamlit's cache for relevant data
                    st.success("yfinance cache cleared. Data will be re-fetched on demand.")
        with col3:
            # Assuming StatscanService exists and has clear_cache
            # if st.button("Refresh Stats Canada Data", key="refresh_statscan", use_container_width=True):
            #     with st.spinner("Refreshing Stats Canada data..."):
            #         statscan_service.clear_cache()
            #         st.cache_data.clear()
            #         st.success("Stats Canada cache cleared. Data will be re-fetched on demand.")
            pass # Placeholder if StatscanService is not ready

        st.markdown("---")
        if st.button("Clear ALL Streamlit Caches (Full Refresh)", key="clear_all_st_caches", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
            st.success("All Streamlit caches cleared. Page will re-run and re-fetch all data.")
    else:
        st.info("No cache statistics available yet. Data might not have been fetched or services are not initialized.")

    st.subheader("System Information")
    st.write(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Streamlit Version:** {st.__version__}")
    # Add more system info if needed
