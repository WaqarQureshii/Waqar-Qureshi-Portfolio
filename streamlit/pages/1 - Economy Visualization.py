"""
Economy Visualization Page

Displays key economic indicators from Statistics Canada
"""

import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import your functions
from functions.update_manager import UpdateManager
from functions.statscan_api import StatsCanAPI
from functions.tables_config import get_table_config, get_tables_by_category

# Page configuration
st.set_page_config(
    page_title="Economic Indicators",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Canadian Economic Indicators")
st.markdown("Real-time economic data from Statistics Canada")

# Initialize services (cached so it only runs once)
@st.cache_resource
def init_services():
    """Initialize API and update manager"""
    api = StatsCanAPI()
    manager = UpdateManager(db=None, api=api)  # db=None uses local storage only
    return manager

manager = init_services()

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Table selection
    economy_tables = get_tables_by_category("economy")
    
    table_options = {
        config["name"]: friendly_name 
        for friendly_name, config in economy_tables.items()
    }
    
    selected_table_name = st.selectbox(
        "Select Dataset",
        options=list(table_options.keys()),
        index=0
    )
    
    selected_table = table_options[selected_table_name]
    
    # Refresh button
    force_refresh = st.button("🔄 Refresh Data", help="Force fetch latest data from StatsCan")
    
    # Show cache info
    with st.expander("📦 Cache Information"):
        cache_info = manager.get_cache_info(selected_table)
        st.json(cache_info)

# Main content area
try:
    # Load data with progress indicator
    with st.spinner(f"Loading {selected_table_name}..."):
        df = manager.get_or_fetch_data(selected_table, force_refresh=force_refresh)
    
    # Get metadata for display
    config = get_table_config(selected_table)
    metadata = manager.get_cached_metadata(config["pid"])
    
    # Display metadata in info boxes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    
    with col2:
        if metadata:
            st.metric("Last Release", metadata.get("releaseTime", "N/A")[:10])
    
    with col3:
        if metadata:
            data_period = f"{metadata.get('cubeStartDate', 'N/A')[:4]} - {metadata.get('cubeEndDate', 'N/A')[:4]}"
            st.metric("Data Period", data_period)
    
    with col4:
        st.metric("Columns", len(df.columns))
    
    # Display description
    st.info(f"**{config['name']}**: {config['description']}")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Visualization", "📋 Data Table", "ℹ️ Metadata"])
    
    with tab1:
        st.subheader("Data Visualization")
        
        # Example visualization for GDP data
        if "provincial_gdp" in selected_table or "gdp" in selected_table.lower():
            # Try to create a time series visualization
            if "REF_DATE" in df.columns and "VALUE" in df.columns:
                # Get unique geographic areas
                if "GEO" in df.columns:
                    geo_options = df["GEO"].unique().to_list()
                    selected_geos = st.multiselect(
                        "Select Regions",
                        geo_options,
                        default=geo_options[:3] if len(geo_options) >= 3 else geo_options
                    )
                    
                    # Filter data
                    filtered_df = df.filter(pl.col("GEO").is_in(selected_geos))
                    
                    # Convert to pandas for plotly
                    plot_df = filtered_df.to_pandas()
                    
                    # Create line chart
                    fig = px.line(
                        plot_df,
                        x="REF_DATE",
                        y="VALUE",
                        color="GEO",
                        title=f"{selected_table_name} Over Time",
                        labels={"VALUE": "Value", "REF_DATE": "Date", "GEO": "Region"}
                    )
                    
                    fig.update_layout(
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Simple time series without geography
                    plot_df = df.to_pandas()
                    
                    fig = px.line(
                        plot_df,
                        x="REF_DATE",
                        y="VALUE",
                        title=f"{selected_table_name} Over Time"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("This dataset doesn't have standard REF_DATE/VALUE columns for automatic visualization.")
                st.write("Available columns:", df.columns)
        
        # For CPI
        elif "cpi" in selected_table.lower():
            if "REF_DATE" in df.columns and "VALUE" in df.columns:
                # CPI visualization
                plot_df = df.to_pandas()
                
                fig = px.line(
                    plot_df,
                    x="REF_DATE",
                    y="VALUE",
                    title="Consumer Price Index Over Time",
                    labels={"VALUE": "CPI Value", "REF_DATE": "Date"}
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate inflation rate if we have enough data
                if len(plot_df) > 12:
                    st.subheader("Year-over-Year Inflation Rate")
                    # This is a simplified calculation - you'd want to do this properly with Polars
                    st.info("📈 Inflation rate calculation would go here")
        
        else:
            st.info("Custom visualization for this dataset is not yet configured. See the Data Table tab to explore the data.")
    
    with tab2:
        st.subheader("Raw Data")
        
        # Display options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search in data", "")
        
        with col2:
            n_rows = st.number_input("Rows to display", min_value=10, max_value=10000, value=100, step=100)
        
        # Filter and display
        display_df = df.head(n_rows)
        
        if search_term:
            # Simple search across all string columns
            mask = pl.lit(False)
            for col in df.columns:
                if df[col].dtype == pl.Utf8:
                    mask = mask | df[col].str.contains(search_term, literal=True)
            
            display_df = df.filter(mask).head(n_rows)
            st.write(f"Found {len(display_df)} matching rows (showing first {n_rows})")
        
        # Display dataframe
        st.dataframe(
            display_df.to_pandas(),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv_data = df.write_csv()
        st.download_button(
            label="📥 Download Full Dataset as CSV",
            data=csv_data,
            file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("Dataset Metadata")
        
        if metadata:
            # Display metadata in organized sections
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Table Information**")
                st.write(f"**Product ID (PID):** {metadata.get('productId', 'N/A')}")
                st.write(f"**CANSIM ID:** {metadata.get('cansimId', 'N/A')}")
                st.write(f"**Title (EN):** {metadata.get('cubeTitleEn', 'N/A')}")
                st.write(f"**Title (FR):** {metadata.get('cubeTitleFr', 'N/A')}")
                st.write(f"**Frequency:** {metadata.get('frequencyCode', 'N/A')}")
                st.write(f"**Archived:** {'Yes' if metadata.get('archived') == '1' else 'No'}")
            
            with col2:
                st.markdown("**Data Coverage**")
                st.write(f"**Start Date:** {metadata.get('cubeStartDate', 'N/A')}")
                st.write(f"**End Date:** {metadata.get('cubeEndDate', 'N/A')}")
                st.write(f"**Total Series:** {metadata.get('nbSeriesCube', 'N/A'):,}")
                st.write(f"**Total Data Points:** {metadata.get('nbDatapointsCube', 'N/A'):,}")
                st.write(f"**Release Time:** {metadata.get('releaseTime', 'N/A')}")
                st.write(f"**Cached At:** {metadata.get('cached_at', 'N/A')[:19]}")
            
            # Show dimensions if available
            if 'dimension' in metadata:
                st.markdown("**Dimensions**")
                for dim in metadata['dimension']:
                    st.write(f"- {dim.get('dimensionNameEn', 'Unknown')} ({len(dim.get('member', []))} members)")
            
            # Full metadata in expander
            with st.expander("📄 View Full Metadata JSON"):
                st.json(metadata)
        else:
            st.warning("No metadata available yet. Try refreshing the data.")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.exception(e)

# Footer
st.divider()
st.caption("Data source: Statistics Canada | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))