"""
Canadian Economic Data Platform - Home Page

Main entry point for the Streamlit application.
"""

import streamlit as st
from config import get_all_categories, DATASETS
from functions import get_data_manager, test_firebase_connection

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Canadian Economic Data Platform",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.image("https://www.canada.ca/etc/designs/canada/wet-boew/assets/sig-blk-en.svg", width=200)
    st.title("🍁 Canadian Data Platform")
    
    st.markdown("---")
    
    st.subheader("📊 Available Categories")
    categories = get_all_categories()
    for category in categories:
        datasets_in_category = [d for d in DATASETS.values() if d.category == category]
        st.markdown(f"**{category}** ({len(datasets_in_category)} datasets)")
    
    st.markdown("---")
    
    # Cache status in sidebar
    try:
        manager = get_data_manager()
        cache_status = manager.get_cache_status()
        
        st.subheader("💾 Cache Status")
        st.metric("Tables Cached", cache_status["total_tables"])
        st.metric("Total Rows", f"{cache_status['total_rows']:,}")
        st.metric("Storage Size", f"{cache_status['total_size_mb']} MB")
        
        if cache_status["updates_available"] > 0:
            st.warning(f"⚠️ {cache_status['updates_available']} updates available")
        else:
            st.success("✅ All data current")
            
    except Exception as e:
        st.error(f"Could not load cache status: {str(e)}")
    
    st.markdown("---")
    st.caption("Data source: Statistics Canada")
    st.caption("Built with Streamlit + Polars + Firebase")

# =============================================================================
# MAIN CONTENT
# =============================================================================

st.title("🍁 Canadian Economic Data Platform")
st.markdown("### Interactive Exploration of Canadian Economic Indicators")

st.markdown("""
Welcome to the Canadian Economic Data Platform! This application provides 
interactive visualizations and analysis of key Canadian economic indicators 
from Statistics Canada.

**Features:**
- 📈 Real-time data from Statistics Canada's API
- 💾 Intelligent caching system for fast performance
- 🔄 Automatic update detection
- 🗺️ Geographic breakdowns (provinces, territories)
- 📊 Interactive charts and data exploration
- 📥 Data export capabilities
""")

st.markdown("---")

# =============================================================================
# DATASET OVERVIEW
# =============================================================================

st.header("📚 Available Datasets")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏦 Economy")
    economy_datasets = [d for d in DATASETS.values() if d.category == "Economy"]
    for dataset in economy_datasets:
        with st.expander(f"📊 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")
    
    st.subheader("🏠 Housing")
    housing_datasets = [d for d in DATASETS.values() if d.category == "Housing"]
    for dataset in housing_datasets:
        with st.expander(f"🏠 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")
    
    st.subheader("👥 Demographics")
    demographics_datasets = [d for d in DATASETS.values() if d.category == "Demographics"]
    for dataset in demographics_datasets:
        with st.expander(f"👥 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")

with col2:
    st.subheader("👷 Labour Market")
    labour_datasets = [d for d in DATASETS.values() if d.category == "Labour Market"]
    for dataset in labour_datasets:
        with st.expander(f"👷 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")
    
    st.subheader("🚢 Trade")
    trade_datasets = [d for d in DATASETS.values() if d.category == "Trade"]
    for dataset in trade_datasets:
        with st.expander(f"🚢 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")
    
    st.subheader("🏢 Business")
    business_datasets = [d for d in DATASETS.values() if d.category == "Business"]
    for dataset in business_datasets:
        with st.expander(f"🏢 {dataset.name}"):
            st.markdown(f"**{dataset.description}**")
            st.caption(f"Tables: {len(dataset.tables)}")
            for table in dataset.tables:
                st.markdown(f"- {table.description} ({table.frequency})")

st.markdown("---")

# =============================================================================
# SYSTEM STATUS
# =============================================================================

st.header("🔧 System Status")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Firebase Connection")
    
    if st.button("🧪 Test Connection"):
        with st.spinner("Testing Firebase connection..."):
            results = test_firebase_connection()
            
            if results["credentials"]:
                st.success("✅ Credentials valid")
            else:
                st.error("❌ Credentials invalid")
            
            if results["firestore"]:
                st.success("✅ Firestore connected")
            else:
                st.error("❌ Firestore connection failed")
            
            if results["storage"]:
                st.success("✅ Cloud Storage connected")
            else:
                st.error("❌ Cloud Storage connection failed")

with col2:
    st.subheader("Data Updates")
    
    try:
        manager = get_data_manager()
        
        if st.button("🔍 Check for Updates"):
            with st.spinner("Checking for updates..."):
                updates = manager.check_updates_available()
                
                if len(updates) > 0:
                    st.warning(f"⚠️ {len(updates)} table(s) have updates available")
                    for update in updates[:5]:  # Show first 5
                        st.caption(f"- {update['product_id']}: {update['reason']}")
                else:
                    st.success("✅ All cached data is current!")
    except Exception as e:
        st.error(f"Error checking updates: {str(e)}")

st.markdown("---")

# =============================================================================
# GETTING STARTED
# =============================================================================

st.header("🚀 Getting Started")

st.markdown("""
1. **Explore the Data**: Use the sidebar to navigate to different visualization pages
2. **Interactive Parameters**: Each page allows you to filter by geography, date range, and other dimensions
3. **Download Data**: Export filtered data as CSV for your own analysis
4. **Automatic Updates**: Data is checked and updated automatically based on Statistics Canada releases

**Navigation:**
- 📊 **Economy Visualization**: GDP, CPI, Interest Rates
- 👷 **Labour Market**: Employment, unemployment, wages
- 🏠 **Housing**: Housing starts, prices, construction
- And more!

Select a page from the sidebar to begin exploring →
""")

st.markdown("---")
st.caption("Data provided by Statistics Canada | Last updated: Statistics Canada releases data daily at 8:30 AM EST")