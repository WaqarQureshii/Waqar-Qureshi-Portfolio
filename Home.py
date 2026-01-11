"""
Portfolio Webapp - Homepage
Author: Waqar Qureshi
"""
import streamlit as st
import polars as pl

# Auth imports
from src.auth.google_auth import initialize_auth_state
from src.auth.permissions import is_admin
from src.components.auth_ui import render_auth_sidebar, render_user_list_table

# Service imports for admin dashboard
from src.data.cache_manager import CacheManager
from src.services.fred_api import FredService
from src.services.yfinance_service import YFinanceService
# from src.services.statscan_api import StatscanService # Uncomment if needed
from src.components.admin import render_admin_dashboard # New import

# Page configuration
st.set_page_config(
    page_title="Portfolio | Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication state
initialize_auth_state()

# Initialize services (these are used by the admin dashboard)
@st.cache_resource
def get_cache_manager():
    return CacheManager()

@st.cache_resource
def get_fred_service():
    return FredService()

@st.cache_resource
def get_yfinance_service():
    return YFinanceService()

# @st.cache_resource
# def get_statscan_service(): # Uncomment if StatsCanService is needed
#     return StatscanService()

cache = get_cache_manager()
fred = get_fred_service()
yf_service = get_yfinance_service()
# statscan_service = get_statscan_service() # Uncomment if StatsCanService is needed

from src.auth.permissions import is_admin
from src.components.auth_ui import render_auth_sidebar, render_user_list_table

# Page configuration
st.set_page_config(
    page_title="Portfolio | Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication state
initialize_auth_state()

# Main content
st.title("Welcome to My Portfolio!")

st.markdown("""
## 👋 About This Project

This is a **placeholder homepage** for you to customize with:
- Information about yourself
- Your background and experience
- What this portfolio project is intended to demonstrate
- Navigation guide for visitors

---

## 📑 Available Pages

Navigate using the sidebar to explore:

1. **Quantitative & Qualitative Analysis**
   - Economic data from FRED (US Federal Reserve)
   - Canadian statistics from Stats Canada
   - Equity data from yfinance
   - Interactive charts and visualizations

2. **Equity Value Playroom**
   - Strategy Backtester (coming soon)
   - Equity Simulator (coming soon)
   - Returns Explorer (coming soon)
   - Technical Sandbox (coming soon)

---

## 🚧 Development Status

**Phase 0: Project Setup** ✅ Complete
- Clean project structure established
- Firebase and API credentials configured
- Ready for feature development

**Phase 1: Firebase Caching Foundation** 🔨 In Progress
- Configuration module created
- Multi-source Firebase service implemented
- Smart cache manager with get-or-fetch logic
- Testing infrastructure below

---

*Feel free to customize this homepage with your own content, styling, and layout!*
""")

# =============================================================================
# PHASE 1 TESTING SECTION
# =============================================================================

with st.expander("🧪 Phase 1: Firebase & Cache Testing", expanded=False):
    st.markdown("### Configuration & Connection Tests")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Test Configuration Loading"):
            with st.spinner("Testing configuration..."):
                try:
                    from src.config.settings import verify_all_configs

                    config_status = verify_all_configs()

                    st.write("**Configuration Status:**")
                    for section, status in config_status.items():
                        if status:
                            st.success(f"✓ {section.title()} configuration loaded")
                        else:
                            st.error(f"✗ {section.title()} configuration missing")

                    if all(config_status.values()):
                        st.success("✅ All configurations valid!")
                    else:
                        st.warning("⚠ Some configurations are missing")

                except Exception as e:
                    st.error(f"Configuration test failed: {str(e)}")

    with col2:
        if st.button("Test Firebase Connection"):
            with st.spinner("Testing Firebase connection..."):
                try:
                    from src.services.firebase_service import test_firebase_connection

                    results = test_firebase_connection()

                    st.write("**Connection Test Results:**")
                    if results["credentials"]:
                        st.success("✓ Credentials valid")
                    else:
                        st.error("✗ Credentials invalid")

                    if results["firestore"]:
                        st.success("✓ Firestore connected")
                    else:
                        st.error("✗ Firestore connection failed")

                    if results["storage"]:
                        st.success("✓ Cloud Storage connected")
                    else:
                        st.error("✗ Cloud Storage connection failed")

                    if all(results.values()):
                        st.success("✅ All connections successful!")
                    else:
                        st.error("✗ Some connections failed")

                except Exception as e:
                    st.error(f"Connection test failed: {str(e)}")

    st.markdown("---")
    st.markdown("### Data Storage & Retrieval Tests")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("Test Data Save/Load"):
            with st.spinner("Testing data operations..."):
                try:
                    import polars as pl
                    from src.services.firebase_service import FirebaseService

                    # Create test data
                    test_data = pl.DataFrame({
                        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                        "value": [100.0, 101.5, 99.8]
                    })

                    firebase = FirebaseService()

                    # Test save
                    test_metadata = {
                        "test": True,
                        "description": "Test dataset"
                    }

                    result = firebase.save_data_complete(
                        source="fred",
                        source_id="_test_series",
                        data=test_data,
                        metadata=test_metadata
                    )

                    if result["status"] == "success":
                        st.success(f"✓ Data saved: {result['row_count']} rows")
                        st.code(f"Storage path: {result['storage_path']}")

                        # Test load
                        loaded_data = firebase.load_data_complete("fred", "_test_series")

                        if loaded_data is not None:
                            st.success(f"✓ Data loaded: {len(loaded_data)} rows")
                            st.dataframe(loaded_data, use_container_width=True)

                            # Cleanup
                            firebase.delete_metadata("fred", "_test_series")
                            firebase.delete_data_from_storage(result['storage_path'])
                            st.info("🗑 Test data cleaned up")
                        else:
                            st.error("✗ Failed to load data")
                    else:
                        st.error(f"✗ Failed to save: {result.get('error')}")

                except Exception as e:
                    st.error(f"Data operation test failed: {str(e)}")

    with col4:
        if st.button("Test Cache Manager"):
            with st.spinner("Testing cache manager..."):
                try:
                    import polars as pl
                    from src.data.cache_manager import CacheManager

                    cache = CacheManager()

                    # Define fetch function
                    def fetch_test_data():
                        return pl.DataFrame({
                            "date": ["2024-01-01", "2024-01-02"],
                            "value": [42.0, 43.5]
                        })

                    # Define metadata function
                    def get_test_metadata():
                        return {"units": "Test Units", "description": "Cache test"}

                    # First call should fetch
                    st.info("First call (should fetch)...")
                    data1 = cache.get_or_fetch(
                        source="fred",
                        source_id="_cache_test",
                        fetch_fn=fetch_test_data,
                        frequency="daily",
                        metadata_fn=get_test_metadata,
                        force_refresh=True
                    )
                    st.success(f"✓ Fetched {len(data1)} rows")

                    # Second call should use cache
                    st.info("Second call (should use cache)...")
                    data2 = cache.get_or_fetch(
                        source="fred",
                        source_id="_cache_test",
                        fetch_fn=fetch_test_data,
                        frequency="daily",
                        metadata_fn=get_test_metadata
                    )
                    st.success(f"✓ Retrieved {len(data2)} rows from cache")

                    # Show cache info
                    cache_info = cache.get_cache_info("fred", "_cache_test")
                    if cache_info:
                        st.write("**Cache Info:**")
                        st.json(cache_info)

                    # Cleanup
                    cache.invalidate("fred", "_cache_test")
                    st.info("🗑 Test cache cleaned up")

                except Exception as e:
                    st.error(f"Cache manager test failed: {str(e)}")

    st.markdown("---")
    st.markdown("### Cache Statistics")

    if st.button("Show Cache Statistics"):
        with st.spinner("Loading cache statistics..."):
            try:
                from src.data.cache_manager import CacheManager

                cache = CacheManager()
                stats = cache.get_stats()

                st.write("**Overall Cache Statistics:**")

                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                with col_stats1:
                    st.metric("Total Datasets", stats.get("total_datasets", 0))
                with col_stats2:
                    st.metric("Total Rows", f"{stats.get('total_rows', 0):,}")
                with col_stats3:
                    st.metric("Total Files", stats.get("total_files", 0))
                with col_stats4:
                    st.metric("Storage Size", f"{stats.get('total_size_mb', 0):.2f} MB")

                # Show per-source breakdown if available
                if "by_source" in stats:
                    st.write("**By Data Source:**")
                    source_df = pl.DataFrame([
                        {
                            "Source": source.upper(),
                            "Datasets": data["datasets"],
                            "Rows": f"{data['rows']:,}"
                        }
                        for source, data in stats["by_source"].items()
                    ])
                    st.dataframe(source_df, use_container_width=True)

            except Exception as e:
                st.error(f"Failed to load cache statistics: {str(e)}")

# =============================================================================
# PHASE 3 TESTING SECTION
# =============================================================================

with st.expander("🧪 Phase 3: FRED API Integration Testing", expanded=False):
    st.markdown("### FRED API & Cache Integration Tests")

    st.info("""
    **Test Objectives:**
    - Verify FRED API connectivity and data fetching
    - Demonstrate intelligent caching with freshness detection
    - Show timing improvements from caching
    - Test error handling and fallback mechanisms
    """)

    # Test 1: Single Series Fetch
    st.markdown("#### Test 1: Single Series Fetch (DGS10)")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Fetch DGS10 (Fresh)", key="fetch_dgs10_fresh"):
            with st.spinner("Fetching 10-Year Treasury data..."):
                try:
                    import time
                    from src.services.fred_api import FredService
                    from src.data.cache_manager import CacheManager

                    fred = FredService()
                    cache = CacheManager()

                    # Time the fetch
                    start_time = time.time()

                    data = cache.get_or_fetch(
                        source="fred",
                        source_id="DGS10",
                        fetch_fn=lambda: fred.get_series("DGS10"),
                        frequency="daily",
                        metadata_fn=lambda: fred.get_series_metadata("DGS10"),
                        force_refresh=True
                    )

                    elapsed = time.time() - start_time

                    st.success(f"[OK] Fetched {len(data):,} rows in {elapsed:.2f}s")
                    st.dataframe(data.tail(10))

                    # Show metadata
                    cache_info = cache.get_cache_info("fred", "DGS10")
                    if cache_info:
                        st.json(cache_info)

                except Exception as e:
                    st.error(f"Fetch failed: {str(e)}")

    with col2:
        if st.button("Load DGS10 (Cached)", key="fetch_dgs10_cached"):
            with st.spinner("Loading from cache..."):
                try:
                    import time
                    from src.services.fred_api import FredService
                    from src.data.cache_manager import CacheManager

                    fred = FredService()
                    cache = CacheManager()

                    start_time = time.time()

                    data = cache.get_or_fetch(
                        source="fred",
                        source_id="DGS10",
                        fetch_fn=lambda: fred.get_series("DGS10"),
                        frequency="daily",
                        metadata_fn=lambda: fred.get_series_metadata("DGS10")
                    )

                    elapsed = time.time() - start_time

                    st.success(f"[OK] Loaded {len(data):,} rows in {elapsed:.2f}s (from cache)")
                    if elapsed < 3.0:
                        st.info(f"**Cache active** - Loading from Firebase Cloud Storage")
                    else:
                        st.warning("Slower than expected - check network connection")

                    cache_info = cache.get_cache_info("fred", "DGS10")
                    if cache_info:
                        is_fresh = cache_info.get("is_fresh", False)
                        age = cache_info.get("age_hours", 0)
                        st.write(f"Cache status: {'[OK] Fresh' if is_fresh else '[WARN] Stale'}")
                        st.write(f"Cache age: {age:.1f} hours")

                except Exception as e:
                    st.error(f"Load failed: {str(e)}")

    st.markdown("---")

    # Test 2: Multi-Series Fetch
    st.markdown("#### Test 2: Treasury Yield Curve")

    if st.button("Fetch Yield Curve (2Y, 5Y, 10Y, 30Y)", key="fetch_yield_curve"):
        with st.spinner("Fetching treasury yields..."):
            try:
                from src.services.fred_api import FredService
                from src.data.cache_manager import CacheManager
                from src.data.fred_datasets import get_category
                import plotly.graph_objects as go

                fred = FredService()
                cache = CacheManager()

                # Get interest rates category
                ir_category = get_category("interest_rates")
                if not ir_category:
                    st.error("Interest rates category not found")
                else:
                    series_ids = ir_category.get_series_ids()

                    st.info(f"Fetching {len(series_ids)} series: {', '.join(series_ids)}")

                    # Fetch each series through cache
                    all_data = {}
                    for series_id in series_ids:
                        data = cache.get_or_fetch(
                            source="fred",
                            source_id=series_id,
                            fetch_fn=lambda sid=series_id: fred.get_series(sid),
                            frequency="daily",
                            metadata_fn=lambda sid=series_id: fred.get_series_metadata(sid)
                        )
                        all_data[series_id] = data

                    st.success(f"[OK] Fetched {len(all_data)} series")

                    # Plot yield curve
                    fig = go.Figure()

                    for series_id, data in all_data.items():
                        # Get last 90 days
                        recent_data = data.tail(90)
                        fig.add_trace(go.Scatter(
                            x=recent_data["date"],
                            y=recent_data["value"],
                            name=series_id,
                            mode="lines"
                        ))

                    fig.update_layout(
                        title="US Treasury Yields (Last 90 Days)",
                        xaxis_title="Date",
                        yaxis_title="Yield (%)",
                        hovermode="x unified",
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Multi-series fetch failed: {str(e)}")

    st.markdown("---")

    # Test 3: Cache Statistics
    st.markdown("#### Test 3: FRED Cache Statistics")

    if st.button("Show FRED Cache Stats", key="fred_cache_stats"):
        try:
            from src.data.cache_manager import CacheManager
            import polars as pl

            cache = CacheManager()

            # Get all FRED cache info
            fred_cache_list = cache.get_all_cache_info(source="fred")

            if fred_cache_list:
                st.success(f"Found {len(fred_cache_list)} cached FRED series")

                # Convert to DataFrame for display
                cache_df = pl.DataFrame([
                    {
                        "Series ID": info["source_id"],
                        "Rows": info["row_count"],
                        "Age (hours)": round(info["age_hours"], 1),
                        "Status": "[OK] Fresh" if info["is_fresh"] else "[WARN] Stale",
                        "Frequency": info["frequency"]
                    }
                    for info in fred_cache_list
                ])

                st.dataframe(cache_df)

                # Overall stats
                stats = cache.get_stats(source="fred")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Series", stats.get("total_datasets", 0))
                with col_stat2:
                    st.metric("Total Rows", f"{stats.get('total_rows', 0):,}")
                with col_stat3:
                    st.metric("Storage Size", f"{stats.get('total_size_mb', 0):.2f} MB")
            else:
                st.info("No FRED data cached yet. Run tests above to populate cache.")

        except Exception as e:
            st.error(f"Failed to load cache stats: {str(e)}")


# =============================================================================
# PHASE 4 TESTING SECTION
# =============================================================================

with st.expander("🧪 Phase 4: Stats Canada & yfinance Integration Testing", expanded=False):
    st.markdown("### Stats Canada & yfinance API Integration Tests")

    st.info("""
    **Test Objectives:**
    - Verify yfinance integration with cache manager
    - Test Stats Canada table fetching and data transformation
    - Demonstrate multi-ticker comparison with visualizations
    - Confirm unified cache statistics across all three sources
    """)

    # Test 1: yfinance Stock History
    st.markdown("#### Test 1: yfinance Stock History (AAPL)")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Fetch AAPL (Fresh)", key="fetch_aapl_fresh"):
            with st.spinner("Fetching Apple stock data..."):
                try:
                    import time
                    from src.services.yfinance_service import YFinanceService
                    from src.data.cache_manager import CacheManager

                    yf_service = YFinanceService()
                    cache = CacheManager()

                    # Time the fetch
                    start_time = time.time()

                    def fetch_aapl():
                        return yf_service.get_ticker_history("AAPL", period="1y", interval="1d")

                    data = cache.get_or_fetch(
                        source="yfinance",
                        source_id="AAPL",
                        fetch_fn=fetch_aapl,
                        frequency="1d",
                        metadata_fn=lambda: {"ticker": "AAPL", "period": "1y"},
                        force_refresh=True
                    )

                    elapsed = time.time() - start_time

                    st.success(f"[OK] Fetched {len(data):,} rows in {elapsed:.2f}s")
                    st.write(f"**Columns:** {', '.join(data.columns)}")
                    st.dataframe(data.tail(10), use_container_width=True)

                except Exception as e:
                    st.error(f"Fetch failed: {str(e)}")

    with col2:
        if st.button("Load AAPL (Cached)", key="fetch_aapl_cached"):
            with st.spinner("Loading from cache..."):
                try:
                    import time
                    from src.services.yfinance_service import YFinanceService
                    from src.data.cache_manager import CacheManager

                    yf_service = YFinanceService()
                    cache = CacheManager()

                    start_time = time.time()

                    def fetch_aapl():
                        return yf_service.get_ticker_history("AAPL", period="1y", interval="1d")

                    data = cache.get_or_fetch(
                        source="yfinance",
                        source_id="AAPL",
                        fetch_fn=fetch_aapl,
                        frequency="1d"
                    )

                    elapsed = time.time() - start_time

                    st.success(f"[OK] Loaded {len(data):,} rows in {elapsed:.2f}s")

                    if elapsed < 3.0:
                        st.info(f"**Cache active** - Loading from Firebase Cloud Storage")

                    cache_info = cache.get_cache_info("yfinance", "AAPL")
                    if cache_info:
                        is_fresh = cache_info.get("is_fresh", False)
                        age = cache_info.get("age_hours", 0)
                        st.write(f"Cache status: {'[OK] Fresh' if is_fresh else '[WARN] Stale'}")
                        st.write(f"Cache age: {age:.1f} hours")

                except Exception as e:
                    st.error(f"Load failed: {str(e)}")

    st.markdown("---")

    # Test 2: Stats Canada GDP Table
    st.markdown("#### Test 2: Stats Canada GDP Data (36100434)")

    if st.button("Fetch GDP by Industry (Last 12 Months)", key="fetch_statscan_gdp"):
        with st.spinner("Fetching Stats Canada GDP data..."):
            try:
                import time
                from src.services.statscan_api import StatsCanService
                from src.data.cache_manager import CacheManager
                from src.data.statscan_datasets import get_table_config

                sc_service = StatsCanService()
                cache = CacheManager()

                # Get table configuration with default vectors
                table_config = get_table_config("36100434")
                if not table_config or not table_config.default_vectors:
                    st.error("GDP table configuration not found or missing default vectors")
                else:
                    st.info(f"Using {len(table_config.default_vectors)} default vectors for {table_config.name}")

                    # Fetch metadata first
                    metadata = sc_service.get_cube_metadata("36100434")
                    if metadata:
                        st.write("**Table Metadata:**")
                        metadata_display = {
                            "Title": metadata.get("cubeTitleEn"),
                            "Frequency": metadata.get("frequencyCode"),
                            "Date Range": f"{metadata.get('cubeStartDate')} to {metadata.get('cubeEndDate')}",
                            "Series Count": metadata.get("nbSeriesCube")
                        }
                        st.json(metadata_display)

                    # Fetch table data with default vectors
                    start_time = time.time()

                    def fetch_gdp():
                        return sc_service.get_table_data(
                            "36100434",
                            latest_n_periods=12,
                            vectors=table_config.default_vectors
                        )

                    data = cache.get_or_fetch(
                        source="statscan",
                        source_id="36100434",
                        fetch_fn=fetch_gdp,
                        frequency="monthly",
                        metadata_fn=lambda: {
                            "product_id": "36100434",
                            "title": metadata.get("cubeTitleEn") if metadata else "GDP by Industry",
                            "vectors": table_config.default_vectors
                        },
                        force_refresh=True
                    )

                    elapsed = time.time() - start_time

                    st.success(f"[OK] Fetched in {elapsed:.2f}s")
                    st.write(f"**Shape:** {data.shape[0]} rows × {data.shape[1]} columns")
                    st.write(f"**Vector Columns:** {data.shape[1] - 1} (format: v{'{vector_id}'})")
                    st.write(f"**Vectors:** {', '.join([f'v{v}' for v in table_config.default_vectors])}")
                    st.dataframe(data.head(10), use_container_width=True)

            except Exception as e:
                st.error(f"Fetch failed: {str(e)}")

    st.markdown("---")

    # Test 3: Multi-Ticker Comparison
    st.markdown("#### Test 3: Multi-Ticker Comparison")

    tickers_selected = st.multiselect(
        "Select tickers to compare",
        ["AAPL", "MSFT", "GOOGL", "^GSPC", "^VIX"],
        default=["AAPL", "MSFT"],
        key="multi_ticker_select"
    )

    if st.button("Compare Tickers", key="compare_tickers") and tickers_selected:
        with st.spinner(f"Fetching {len(tickers_selected)} tickers..."):
            try:
                from src.services.yfinance_service import YFinanceService
                from src.data.cache_manager import CacheManager
                import plotly.graph_objects as go

                yf_service = YFinanceService()
                cache = CacheManager()

                # Fetch all tickers
                all_data = {}
                for ticker in tickers_selected:
                    data = cache.get_or_fetch(
                        source="yfinance",
                        source_id=ticker,
                        fetch_fn=lambda t=ticker: yf_service.get_ticker_history(t, period="6mo"),
                        frequency="1d"
                    )
                    all_data[ticker] = data

                st.success(f"[OK] Fetched {len(all_data)} tickers")

                # Create normalized comparison chart (base = 100)
                fig = go.Figure()

                for ticker, data in all_data.items():
                    # Normalize to base 100 (first closing price)
                    first_close = data["close"][0]
                    normalized = (data["close"] / first_close * 100)

                    fig.add_trace(go.Scatter(
                        x=data["date"],
                        y=normalized,
                        mode="lines",
                        name=ticker
                    ))

                fig.update_layout(
                    title="Normalized Price Comparison (Base = 100)",
                    xaxis_title="Date",
                    yaxis_title="Normalized Price",
                    hovermode="x unified",
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Multi-ticker comparison failed: {str(e)}")

    st.markdown("---")

    # Test 4: Unified Cache Statistics
    st.markdown("#### Test 4: Unified Cache Statistics")

    if st.button("Show All Cache Stats", key="all_cache_stats"):
        try:
            from src.data.cache_manager import CacheManager
            import polars as pl

            cache = CacheManager()

            # Get stats by source
            st.write("**Cache Statistics by Source:**")

            for source in ["fred", "yfinance", "statscan"]:
                st.subheader(f"{source.upper()} Cache")
                stats = cache.get_stats(source=source)

                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Datasets", stats.get("total_datasets", 0))
                with col_s2:
                    st.metric("Total Rows", f"{stats.get('total_rows', 0):,}")
                with col_s3:
                    st.metric("Storage", f"{stats.get('total_size_mb', 0):.2f} MB")

            st.markdown("---")

            # Get detailed cache inventory
            st.write("**Detailed Cache Inventory:**")
            all_info = cache.get_all_cache_info()

            if all_info:
                cache_df = pl.DataFrame([
                    {
                        "Source": info["source"].upper(),
                        "ID": info["source_id"],
                        "Rows": info["row_count"],
                        "Age (hrs)": round(info["age_hours"], 1),
                        "Status": "[OK] Fresh" if info["is_fresh"] else "[WARN] Stale",
                        "Frequency": info["frequency"]
                    }
                    for info in all_info
                ])
                st.dataframe(cache_df, use_container_width=True)
            else:
                st.info("No cached data found. Run tests above to populate cache.")

        except Exception as e:
            st.error(f"Failed to load cache stats: {str(e)}")


# Admin Dashboard Section
if st.session_state.get("authenticated") and is_admin(): # Check if user is authenticated and admin
    st.markdown("---")
    # Using a expander for the admin dashboard to keep the homepage clean
    with st.expander("👑 Admin Dashboard", expanded=False):
        render_admin_dashboard(cache_manager=cache, fred_service=fred, yf_service=yf_service) #, statscan_service=statscan_service)
        # Optionally display registered users within the admin dashboard
        st.markdown("---")
        st.subheader("👥 Registered Users")
        if st.button("🔄 Refresh User List", key="admin_refresh_users"):
            st.rerun()
        render_user_list_table()

# Sidebar
with st.sidebar:
    # Auth section at top
    render_auth_sidebar()

    st.markdown("---")

    # Navigation
    st.header("Navigation")
    st.info("Use the pages menu above to navigate")

    st.markdown("---")
    st.caption("Built with Streamlit 🎈")
