"""
Quantitative & Qualitative Analysis
FRED, Stats Canada, and yfinance data visualization
"""
import streamlit as st
import polars as pl

from src.data.cache_manager import CacheManager
from src.services.fred_api import FredService
from src.services.yfinance_service import YFinanceService
from src.data.fred_datasets import get_series_config
from src.config.constants import YFINANCE_TICKERS
from src.components.charts import (
    resample_to_monthly,
    resample_to_quarterly,
    calculate_percentage_of_series,
    calculate_ratio,
    calculate_pct_change,
    merge_multiple_series,
    create_bar_line_chart,
    create_dual_axis_chart,
    create_ratio_overlay_chart,
    create_dual_subplot_chart,
    calculate_forward_returns,
    detect_signal_occurrences,
    calculate_signal_metrics,
    create_ratio_overlay_chart_with_signals
)
from src.components.sidebar import (
    render_date_range_selector,
    render_preset_date_ranges,
    render_refresh_controls
)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Analysis | Portfolio",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Quantitative & Qualitative Analysis")
st.markdown("Interactive economic and market data analysis combining FRED, Stats Canada, and yfinance data sources.")

# =============================================================================
# INITIALIZE CACHE MANAGER
# =============================================================================

@st.cache_resource
def get_cache_manager():
    """Initialize CacheManager singleton."""
    return CacheManager()

@st.cache_resource
def get_fred_service():
    """Initialize FredService singleton."""
    return FredService()

@st.cache_resource
def get_yfinance_service():
    """Initialize YFinanceService singleton."""
    return YFinanceService()

cache = get_cache_manager()
fred = get_fred_service()
yf_service = get_yfinance_service()


# =============================================================================
# SIDEBAR CONTROLS
# =============================================================================

with st.sidebar:
    st.header("Data Controls")

    # Date range selector
    start_date, end_date = render_date_range_selector(
        key_prefix="analysis",
        default_years_back=20
    )

    # Preset date ranges
    preset = render_preset_date_ranges("analysis")
    if preset:
        start_date, end_date = preset
        st.rerun()

    st.divider()

    # Refresh controls
    if render_refresh_controls():
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared! Refresh the data using the fetch buttons.")


# =============================================================================
# April 25, 2025: MONEY SUPPLY VS S&P 500
# =============================================================================

@st.fragment
def render_chart1_money_supply_vs_sp500():
    """
    Chart 1: Money Market Funds (bars) as % of GDP vs S&P 500 (line).

    Data Flow:
    1. Fetch MMMFFAQ027S (quarterly), GDP (quarterly) ^GSPC (daily)
    2. Transform all to quarterly basis.
    3. Create Money Market Fund as % of GDP series
    4. Merge series and visualize
    """
    
    st.subheader("We can visually see liquid cash, represented by Money Market Funds flowing into the stock market competing with other sources of investments driving up the S&P 500.")

    st.markdown("""
                **What is the Money Market Funds?**
                
                - The Money Market Funds represents the **Total Financial Assets** held by all Money Market Funds (MMFs) in the United States.

                **What does it measure?**

                - The level (stock) of the total value of all financial assets held by U.S. Money Market Funds at the end of a given period. This includes the value of all the short-term, high-quality, liquid securities they hold.

                **We can see the build up of liquid cash as a % of GDP in July 2006 and January 2019**

                - Prior to corrections, there is a noticeable increase in Money Market Funds as a percentage of GDP. This suggests investors were accumulating cash in anticipation of a market correction or fear.
                - When the market correction occurs, this cash is deployed into the market, providing liquidity and supporting asset prices. This pattern highlights the role of Money Market Funds as a safe haven during periods of market uncertainty, allowing investors to quickly mobilize funds when opportunities arise.

                **Analyst Note:** When we hit that 25% of GDP mark, we often see the bottom of the S&P 500.
                """)
                
    
    st.subheader("💰 Money Supply vs Market Performance")

    col1, col2 = st.columns([5, 1])


    with col2:
        if st.button("Fetch Data", key="chart1_fetch", type="primary", use_container_width=True):
            st.session_state.chart1_fetched = True

        if st.button("Clear Chart", key="chart1_clear", use_container_width=True):
            st.session_state.chart1_fetched = False
            st.rerun()

    if st.session_state.get("chart1_fetched", False):
        try:
            with st.spinner("Fetching M2, GDP, and S&P 500 data..."):
                # Fetch ALL available historical data (no date limits)
                # This ensures cache contains full dataset, then we filter client-side

                # Fetch M2SL from FRED (all historical data)
                moneymarket_fund_config = get_series_config("MMMFFAQ027S")
                moneymarket_fund_df = cache.get_or_fetch(
                    source="fred",
                    source_id="MMMFFAQ027S",
                    fetch_fn=lambda: fred.get_series("MMMFFAQ027S"),
                    frequency=moneymarket_fund_config.frequency,
                    metadata_fn=lambda: fred.get_series_metadata("MMMFFAQ027S"),
                    force_refresh=False
                )
                
                # Fetch GDP from FRED (all historical data)
                gdp_config = get_series_config("GDP")
                gdp_df = cache.get_or_fetch(
                        source="fred",
                        source_id="GDP",
                        fetch_fn=lambda: fred.get_series("GDP"),
                        frequency=gdp_config.frequency,
                        metadata_fn=lambda: fred.get_series_metadata("GDP"),
                        force_refresh=False
                    )

                # Fetch S&P 500 from yfinance (all historical data)
                sp500_df = cache.get_or_fetch(
                    source="yfinance",
                    source_id="^GSPC",
                    fetch_fn=lambda: yf_service.get_ticker_history("^GSPC", period="max", interval="1d"),
                    frequency="daily",
                    metadata_fn=lambda: {"ticker": "^GSPC", "name": "S&P 500"},
                    force_refresh=False
                )

                # Filter ALL data to selected date range (client-side filtering)
                moneymarket_fund_df = moneymarket_fund_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )

                gdp_df = gdp_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )

                sp500_df = sp500_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )

                # Transform data
                # 1. MMMFFAQ027S is already quarterly
                
                # 2. GDP is already quarterly

                # 3. Resample S&P 500 to quarterly
                sp500_df = resample_to_quarterly(
                    sp500_df.select(["date", "close"]),
                    date_col="date",
                    value_col="close",
                    agg_method="last"
                )

                # 4. Convert MMMFFAQ027S to billions to match GDP
                moneymarket_fund_df = moneymarket_fund_df.with_columns([
                    (pl.col("value") / 1000).alias("value")
                ])

                # 5. Money Market Fund as a % of GDP
                moneymarket_fund_df = calculate_percentage_of_series(
                    numerator_df=moneymarket_fund_df.rename({"value": "numerator"}),
                    denominator_df=gdp_df.rename({"value": "denominator"}),
                    date_col="date",
                    num_value_col="numerator",
                    denom_value_col="denominator",
                    result_col="moneymarket_fund_pct_gdp"
                )

                # 6. Merge Money Market Fund % of GDP with S&P 500
                merged_df = merge_multiple_series([
                    (moneymarket_fund_df, "moneymarket_fund_pct_gdp"),
                    (sp500_df, "close")
                ], date_col="date")

                # 7. Rename S&P 500 close column for clarity
                merged_df = merged_df.rename({"close": "sp500"})

                # 8. Visualize
                fig = create_bar_line_chart(
                    df=merged_df,
                    date_col="date",
                    bar_col="moneymarket_fund_pct_gdp",
                    line_col="sp500",
                    bar_name="Money Market Fund as % of GDP",
                    line_name="S&P 500",
                    bar_y_title="Money Market Fund % of GDP",
                    line_y_title="S&P 500 Index",
                    title="Money Market Fund as a % of GDP vs Market Performance (Quarterly)",
                    height=600
                )

                with col1:
                    st.plotly_chart(fig, use_container_width=True)

                st.success("✅ Data loaded successfully!")

        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.exception(e)
    else:
        st.info("👆 Click 'Fetch Data' to load the chart")


# =============================================================================
# April 25, 2025: T-BILL VS INFLATION CHART
# =============================================================================

@st.fragment
def render_chart2_tbill_vs_inflation():
    """
    Chart 2: 3-Month T-Bill Rate vs US Inflation (YoY from CPI).

    Data Flow:
    1. Fetch TB3MS (monthly rate in %)
    2. Fetch CPIAUCSL (monthly CPI index)
    3. Calculate YoY inflation from CPI
    4. Merge and visualize
    """

    st.subheader("But what really drives or incentivizes investors to put cash in the money markets?")

    st.markdown("""
                The basic requirement for investors to park cash in a particular asset would be where they can at *at least* preserve their purchasing power (i.e. beat inflation). If the risk-free rate (T-Bill rate) is below inflation, invesetors are effectively losing money in real terms by holding cash in these bills. The opposite would be true.

                - **April 2020**: During the early stages of the COVID-19 pandemic, the Federal Reserve slashed interest rates to near zero to support the economy. This led to a situation where the 3-Month T-Bill rate fell below inflation, resulting in a negative real interest rate. Investors were disincentivized from holding cash in T-Bills as their purchasing power was eroding, leading to increased risk-taking behavior and a surge in investments in equities and other higher-yielding assets.

                - **April 2025**: We are in a situation where there's record level of cash sitting in Money Market Funds because it currently makes sense to do so with the T-Bill > Inflation. Investors are being compensated for holding cash. However, if inflation were to rise above the T-Bill or if the T-Bill rates were to fall below inflation via FED cuts, we may see a rush of cash leaving these funds to seek higher returns elsewhere, potentially leading to market volatility as this cash floods into riskier assets like stocks and bonds.
                """)
    st.subheader("📈 Risk-Free Rates vs Inflation")

    col1, col3 = st.columns([5, 1])

    with col3:
        if st.button("Fetch Data", key="chart2_fetch", type="primary", use_container_width=True):
            st.session_state.chart2_fetched = True

        if st.button("Clear Chart", key="chart2_clear", use_container_width=True):
            st.session_state.chart2_fetched = False
            st.rerun()

    if st.session_state.get("chart2_fetched", False):
        try:
            with st.spinner("Fetching T-Bill and CPI data..."):
                # Fetch ALL available historical data (no date limits)
                # This ensures cache contains full dataset, then we filter client-side

                # Fetch TB3MS from FRED (all historical data)
                tbill_config = get_series_config("TB3MS")
                tbill_df = cache.get_or_fetch(
                    source="fred",
                    source_id="TB3MS",
                    fetch_fn=lambda: fred.get_series("TB3MS"),
                    frequency=tbill_config.frequency,
                    metadata_fn=lambda: fred.get_series_metadata("TB3MS"),
                    force_refresh=False
                )

                # Fetch CPIAUCSL from FRED (all historical data)
                cpi_config = get_series_config("CPIAUCSL")
                cpi_df = cache.get_or_fetch(
                    source="fred",
                    source_id="CPIAUCSL",
                    fetch_fn=lambda: fred.get_series("CPIAUCSL"),
                    frequency=cpi_config.frequency,
                    metadata_fn=lambda: fred.get_series_metadata("CPIAUCSL"),
                    force_refresh=False
                )

                # Fetch M2SL from FRED (all historical data)
                moneymarket_fund_config = get_series_config("MMMFFAQ027S")
                mmFund_df = cache.get_or_fetch(
                    source="fred",
                    source_id="MMMFFAQ027S",
                    fetch_fn=lambda: fred.get_series("MMMFFAQ027S"),
                    frequency=moneymarket_fund_config.frequency,
                    metadata_fn=lambda: fred.get_series_metadata("MMMFFAQ027S"),
                    force_refresh=False
                )
                # Fetch GDP from FRED (all historical data)
                gdp_config = get_series_config("GDP")
                gdp_df = cache.get_or_fetch(
                        source="fred",
                        source_id="GDP",
                        fetch_fn=lambda: fred.get_series("GDP"),
                        frequency=gdp_config.frequency,
                        metadata_fn=lambda: fred.get_series_metadata("GDP"),
                        force_refresh=False
                    )

                # Filter data to selected date range (client-side filtering)
                tbill_df = tbill_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )
                cpi_df = cpi_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )
                mmFund_df = mmFund_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )
                gdp_df = gdp_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )

                # Transform data
                # 1. Resample T-Bill to quarterly
                tbill_quarterly = resample_to_quarterly(tbill_df, date_col="date", value_col="value", agg_method="last")
                tbill_quarterly = tbill_quarterly.select(["date", "value"]).rename({"value": "tbill_rate"})
                

                # 2. Calculate YoY inflation from CPI
                inflation_df = calculate_pct_change(
                    cpi_df,
                    date_col="date",
                    value_col="value",
                    result_col="inflation_rate",
                    noPeriods=12
                )

                # 3. Resample inflation to quarterly
                cpi_quarterly = resample_to_quarterly(inflation_df, date_col="date", value_col="inflation_rate", agg_method="last")

                # 4. Merge T-Bill and Inflation to calculate real rate
                temp_merged = merge_multiple_series([
                    (tbill_quarterly, "tbill_rate"),
                    (cpi_quarterly, "inflation_rate")
                ], date_col="date")

                # 5. Calculate real rate (T-Bill - Inflation)
                temp_merged = temp_merged.with_columns([
                    (pl.col("tbill_rate") - pl.col("inflation_rate")).alias("real_rate")
                ])

                # 6. Prepare Money Market Fund (rename value column)
                mmFund_df = mmFund_df.with_columns([
                    (pl.col("value") / 1000).alias("value (in Billions)")
                ])

                # 7. Create Money Market Fund as % of GDP
                mmFund_df = calculate_percentage_of_series(
                    numerator_df=mmFund_df.rename({"value (in Billions)": "numerator"}),
                    denominator_df=gdp_df.rename({"value": "denominator"}),
                    date_col="date",
                    num_value_col="numerator",
                    denom_value_col="denominator",
                    result_col="mmFund_pct_gdp"
                )

                # 6. Final merge: T-Bill, Inflation, Real Rate, M2
                merged_df = merge_multiple_series([
                    (temp_merged.select(["date", "tbill_rate"]), "tbill_rate"),
                    (temp_merged.select(["date", "inflation_rate"]), "inflation_rate"),
                    (temp_merged.select(["date", "real_rate"]), "real_rate"),
                    (mmFund_df, "mmFund_pct_gdp")
                ], date_col="date")

                # 7. Visualize with subplot chart
                fig = create_dual_subplot_chart(
                    df=merged_df,
                    date_col="date",
                    # Top subplot - T-Bill vs Inflation
                    top_chart_title="T-Bill Rate vs Inflation",
                    top_left_col="tbill_rate",
                    top_left_name="T-Bill Rate",
                    top_left_title="3-Month T-Bill Rate (%)",
                    top_right_col="inflation_rate",
                    top_right_name="Inflation",
                    top_right_title="Inflation YoY (%)",
                    # Bottom subplot - Real Rate vs Money Market Fund
                    bottom_chart_title="Real Rate vs Money Market Fund",
                    bottom_right_col="real_rate",
                    bottom_right_name="Real Rate",
                    bottom_right_title="Real Rate (Spread) (%)",
                    bottom_right_type="line",
                    bottom_left_col="mmFund_pct_gdp",
                    bottom_left_name="MM Fund/GDP",
                    bottom_left_title="Money Market Fund as % of GDP (%)",
                    bottom_left_type="bar",
                    # General
                    title="Risk-Free Rates vs Inflation with Real Rate & Money Market Funds Analysis",
                    height=900
                )

                with col1:
                    st.plotly_chart(fig, use_container_width=True)

                # Display metrics
                st.subheader("Current Metrics")
                metric_cols = st.columns(4)

                latest_row = merged_df.tail(1).to_dicts()[0]

                with metric_cols[0]:
                    st.metric(
                        "Latest T-Bill Rate",
                        f"{latest_row['tbill_rate']:.2f}%"
                    )

                with metric_cols[1]:
                    st.metric(
                        "Latest Inflation",
                        f"{latest_row['inflation_rate']:.2f}%"
                    )

                with metric_cols[2]:
                    st.metric(
                        "Real Rate (Spread)",
                        f"{latest_row['real_rate']:.2f}%",
                        delta=None,
                        help="T-Bill Rate minus Inflation"
                    )

                with metric_cols[3]:
                    st.metric(
                        "Money Market Fund as % of GDP",
                        f"{latest_row['mmFund_pct_gdp']:.2f}%"
                    )

                st.success("✅ Data loaded successfully!")

        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.exception(e)
    else:
        st.info("👆 Click 'Fetch Data' to load the chart")


# =============================================================================
# RISK ON OR OFF: HYG VS TLT VS S&P 500
# =============================================================================

@st.fragment
def render_chart1_hyg_tlt_vs_sp500():
    """
    Chart 3: HYG/TLT Ratio (risk-on/risk-off) vs S&P 500.

    Data Flow:
    1. Fetch HYG, TLT, ^GSPC (all daily close prices)
    2. Calculate HYG/TLT ratio
    3. Merge with S&P 500
    4. Visualize
    """
    st.subheader("🎲 Signs of if we're Risk on or Risk Off")
    st.markdown("""
    The relationship between HYG (High Yield Corporate Bonds), TLT (20+ Year Treasury Bonds), and the S&P 500 is one of the most important "triangles" in macro analysis. It reveals whether the market is in a "Risk-On" or "Risk-Off" posture and whether investors are more worried about economic growth or interest rates.

    **1. The Core Correlation: HYG is "Equity-Lite"**
    - The most striking correlation is between HYG and the S&P 500. While HYG is technically a bond fund, it behaves more like a stock index.

    - High Positive Correlation: Historically, HYG and the S&P 500 maintain a correlation of roughly 0.60 to 0.75. When stocks go up, high-yield bonds usually go up.

    - The Driver (Credit Spreads): This is because "junk" bonds are issued by companies with weaker balance sheets. If the economy is booming (good for stocks), the risk of these companies defaulting drops, making their bonds more valuable.

    **2. The Defensive Pivot: TLT as the "Safe Haven"**
    TLT typically has a negative or low correlation with both the S&P 500 and HYG.

    - Flight to Quality: In a standard market panic (Risk-Off), investors sell stocks (S&P 500) and junk bonds (HYG) and buy "risk-free" government debt (TLT).

    - Interest Rate Sensitivity: TLT is highly sensitive to interest rates (duration). If rates fall (usually during a recession), TLT price surges.
                
    **Analyst Note:** Watch for "divergence". If the S&P 500 is making new highs but HYG is failing to follow, it suggests that the "smart money" in the bond market is getting nervous about corporate health even while stock investors remain optimistic. The opposite is also true.

    **Notes of divergence**:
    - October 2023: HYG/TLT Ratio hits new highs, but the S&P 500 lags. This divergence suggests investors were willing put in money into high-yield corporate bonds but not the underlying company's equity. Shortly after, the S&P 500 reaches new all-time highs.
                
    - December 2021: The S&P 500 hits new highs, but the HYG/TLT Ratio fails to confirm this move. This divergence indicates that while stock investors were optimistic, bond investors were more cautious about corporate credit risk. Following this divergence, the market experienced increased volatility and a correction in early 2022.
    """)

    # Signal Detection Settings
    with st.expander("⚙️ Signal Detection Settings", expanded=False):
        st.markdown("Configure conditions to identify market signals based on HYG/TLT ratio and S&P 500 movements.")

        # Row 1: Interval
        st.subheader("Lookback Period")
        interval_days = st.number_input(
            "Interval for % Change Calculation (days)",
            min_value=1,
            max_value=252,
            value=7,
            step=1,
            key="chart3_signal_interval",
            help="Number of days over which to calculate percentage changes"
        )

        st.divider()

        # Row 2: HYG/TLT Ratio Conditions
        st.subheader("HYG/TLT Ratio Conditions")
        col_ratio1, col_ratio2 = st.columns(2)

        with col_ratio1:
            ratio_direction = st.radio(
                "HYG/TLT Ratio Direction",
                options=["increase", "decrease"],
                index=0,
                key="chart3_ratio_direction",
                horizontal=True
            )

        with col_ratio2:
            ratio_threshold = st.number_input(
                "Minimum % Change Threshold",
                min_value=0.0,
                max_value=100.0,
                value=2.0,
                step=0.5,
                key="chart3_ratio_threshold",
                help="Minimum percentage change required (absolute value)"
            )

        st.divider()

        # Row 3: S&P 500 Conditions
        st.subheader("S&P 500 Conditions")
        col_sp1, col_sp2 = st.columns(2)

        with col_sp1:
            sp500_direction = st.radio(
                "S&P 500 Direction",
                options=["increase", "decrease"],
                index=1,
                key="chart3_sp500_direction",
                horizontal=True
            )

        with col_sp2:
            sp500_threshold = st.number_input(
                "Minimum % Change Threshold",
                min_value=0.0,
                max_value=100.0,
                value=2.0,
                step=0.5,
                key="chart3_sp500_threshold",
                help="Minimum percentage change required (absolute value)"
            )

        st.divider()

        # Row 4: Forward-Looking Period
        st.subheader("Forward Return Analysis")
        forward_period = st.selectbox(
            "Calculate returns over next N days",
            options=[7, 30, 100],
            index=1,
            key="chart3_forward_period",
            help="Period for calculating forward returns after signal occurrence"
        )

        # Add visual summary
        st.info(
            f"**Signal Summary:** Identify dates where HYG/TLT ratio "
            f"{ratio_direction}s by at least {ratio_threshold}% "
            f"AND S&P 500 {sp500_direction}s by at least {sp500_threshold}% "
            f"over a {interval_days}-day period. "
            f"Calculate returns over the next {forward_period} days."
        )

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("Fetch Data", key="chart3_fetch", type="primary", use_container_width=True):
            st.session_state.chart3_fetched = True

        if st.button("Clear Chart", key="chart3_clear", use_container_width=True):
            st.session_state.chart3_fetched = False
            st.rerun()

    if st.session_state.get("chart3_fetched", False):
        # Read signal detection settings from session state
        interval_days = st.session_state.get("chart3_signal_interval", 7)
        ratio_direction = st.session_state.get("chart3_ratio_direction", "increase")
        ratio_threshold = st.session_state.get("chart3_ratio_threshold", 2.0)
        sp500_direction = st.session_state.get("chart3_sp500_direction", "decrease")
        sp500_threshold = st.session_state.get("chart3_sp500_threshold", 2.0)
        forward_period = st.session_state.get("chart3_forward_period", 30)

        try:
            with st.spinner("Fetching HYG, TLT, and S&P 500 data..."):
                # Calculate period for yfinance (max to get all historical data)
                yf_period = "max"

                # Fetch HYG from yfinance
                # force_refresh=True to invalidate old date-limited cache
                hyg_df = cache.get_or_fetch(
                    source="yfinance",
                    source_id="HYG",
                    fetch_fn=lambda: yf_service.get_ticker_history("HYG", period=yf_period, interval="1d"),
                    frequency="daily",
                    metadata_fn=lambda: {"ticker": "HYG", "name": YFINANCE_TICKERS["HYG"]["name"]},
                    force_refresh=True
                )

                # Fetch TLT from yfinance
                # force_refresh=True to invalidate old date-limited cache
                tlt_df = cache.get_or_fetch(
                    source="yfinance",
                    source_id="TLT",
                    fetch_fn=lambda: yf_service.get_ticker_history("TLT", period=yf_period, interval="1d"),
                    frequency="daily",
                    metadata_fn=lambda: {"ticker": "TLT", "name": YFINANCE_TICKERS["TLT"]["name"]},
                    force_refresh=True
                )

                # Fetch S&P 500 from yfinance
                # force_refresh=True to invalidate old date-limited cache
                sp500_df = cache.get_or_fetch(
                    source="yfinance",
                    source_id="^GSPC",
                    fetch_fn=lambda: yf_service.get_ticker_history("^GSPC", period=yf_period, interval="1d"),
                    frequency="daily",
                    metadata_fn=lambda: {"ticker": "^GSPC", "name": "S&P 500"},
                    force_refresh=True
                )

                # Filter all data to date range
                hyg_df = hyg_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )
                tlt_df = tlt_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )
                sp500_df = sp500_df.filter(
                    (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
                )

                # Transform data
                # 1. Select close prices
                hyg_close = hyg_df.select(["date", "close"]).rename({"close": "hyg"})
                tlt_close = tlt_df.select(["date", "close"]).rename({"close": "tlt"})
                sp500_close = sp500_df.select(["date", "close"]).rename({"close": "sp500"})

                # 2. Calculate HYG/TLT ratio
                ratio_df = calculate_ratio(
                    numerator_df=hyg_close.rename({"hyg": "value"}),
                    denominator_df=tlt_close.rename({"tlt": "value"}),
                    date_col="date",
                    num_value_col="value",
                    denom_value_col="value",
                    result_col="hyg_tlt_ratio"
                )

                # 3. Calculate percentage changes using dynamic interval
                ratio_df = calculate_pct_change(
                    ratio_df,
                    date_col="date",
                    value_col="hyg_tlt_ratio",
                    result_col="ratio_pct_change",
                    noPeriods=interval_days
                )

                sp500_close = calculate_pct_change(
                    sp500_close,
                    date_col="date",
                    value_col="sp500",
                    result_col="sp500_pct_change",
                    noPeriods=interval_days
                )

                # 4. Calculate forward returns on S&P 500
                sp500_close = calculate_forward_returns(
                    sp500_close,
                    value_col="sp500",
                    forward_periods=forward_period,
                    date_col="date",
                    result_col=f"sp500_forward_{forward_period}d"
                )

                # 5. Merge all series including percentage change columns
                merged_df = merge_multiple_series([
                    (ratio_df, "hyg_tlt_ratio"),
                    (ratio_df, "ratio_pct_change"),
                    (sp500_close, "sp500"),
                    (sp500_close, "sp500_pct_change"),
                    (sp500_close, f"sp500_forward_{forward_period}d")
                ], date_col="date")

                # 6. Detect signal occurrences
                merged_df = detect_signal_occurrences(
                    df=merged_df,
                    ratio_col="hyg_tlt_ratio",
                    ratio_pct_col="ratio_pct_change",
                    overlay_col="sp500",
                    overlay_pct_col="sp500_pct_change",
                    ratio_direction=ratio_direction,
                    ratio_threshold=ratio_threshold,
                    overlay_direction=sp500_direction,
                    overlay_threshold=sp500_threshold,
                    date_col="date"
                )

                # 7. Calculate signal metrics
                signal_metrics = calculate_signal_metrics(
                    df=merged_df,
                    signal_col="signal",
                    forward_return_col=f"sp500_forward_{forward_period}d"
                )

                # 8. Visualize with signal markers
                fig = create_ratio_overlay_chart_with_signals(
                    df=merged_df,
                    date_col="date",
                    ratio_col="hyg_tlt_ratio",
                    overlay_col="sp500",
                    signal_col="signal",
                    ratio_pct_col="ratio_pct_change",
                    overlay_pct_col="sp500_pct_change",
                    forward_return_col=f"sp500_forward_{forward_period}d",
                    ratio_name="HYG/TLT Ratio",
                    overlay_name="S&P 500",
                    ratio_y_title="HYG/TLT Ratio",
                    overlay_y_title="S&P 500 Index",
                    title=f"Risk-On/Risk-Off Indicator vs Market - {signal_metrics['count']} Signals Detected",
                    height=600
                )

                with col1:
                    st.plotly_chart(fig, use_container_width=True)

                # Display current market metrics
                st.subheader("Current Market Metrics")
                metric_cols = st.columns(4)

                latest_row = merged_df.tail(1).to_dicts()[0]

                with metric_cols[0]:
                    st.metric(
                        "Latest HYG/TLT Ratio",
                        f"{latest_row['hyg_tlt_ratio']:.4f}"
                    )

                with metric_cols[1]:
                    st.metric(
                        "Latest S&P 500",
                        f"${latest_row['sp500']:,.2f}"
                    )

                with metric_cols[2]:
                    # Calculate trend (is ratio rising?)
                    recent_ratio = merged_df.tail(20)["hyg_tlt_ratio"].mean()
                    older_ratio = merged_df.tail(60).head(20)["hyg_tlt_ratio"].mean()
                    trend = "Risk-On 📈" if recent_ratio > older_ratio else "Risk-Off 📉"
                    st.metric(
                        "20-Day Trend",
                        trend
                    )

                with metric_cols[3]:
                    st.metric(
                        "Data Points",
                        f"{len(merged_df)} days"
                    )

                st.divider()

                # Display signal analysis metrics
                st.subheader(f"Signal Analysis: {forward_period}-Day Forward Returns")

                if signal_metrics["count"] > 0:
                    signal_metric_cols = st.columns(5)

                    with signal_metric_cols[0]:
                        st.metric(
                            "Total Signals",
                            f"{signal_metrics['count']}"
                        )

                    with signal_metric_cols[1]:
                        avg_return = signal_metrics['avg_return']
                        st.metric(
                            "Avg Return",
                            f"{avg_return:+.2f}%",
                            delta=f"{avg_return:+.2f}%"
                        )

                    with signal_metric_cols[2]:
                        st.metric(
                            "Min Return",
                            f"{signal_metrics['min_return']:+.2f}%"
                        )

                    with signal_metric_cols[3]:
                        st.metric(
                            "Max Return",
                            f"{signal_metrics['max_return']:+.2f}%"
                        )

                    with signal_metric_cols[4]:
                        st.metric(
                            "Win Rate",
                            f"{signal_metrics['win_rate']:.1f}%",
                            help="Percentage of signals that had positive returns"
                        )

                    # Add interpretation guidance
                    if signal_metrics['avg_return'] > 0:
                        st.success(
                            f"✅ On average, when these conditions occurred, S&P 500 rose "
                            f"{signal_metrics['avg_return']:.2f}% over the next {forward_period} days."
                        )
                    else:
                        st.warning(
                            f"⚠️ On average, when these conditions occurred, S&P 500 fell "
                            f"{abs(signal_metrics['avg_return']):.2f}% over the next {forward_period} days."
                        )
                else:
                    st.info(
                        f"No signals detected with current settings. Try adjusting the thresholds or interval. "
                        f"Note: Signals within the last {forward_period} days cannot have forward returns calculated."
                    )

                st.divider()

                st.success("✅ Data loaded successfully!")

        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.exception(e)
    else:
        st.info("👆 Click 'Fetch Data' to load the chart")


# =============================================================================
# MAIN PAGE LAYOUT
# =============================================================================

st.divider()

# Create tabs for different analysis sections

with st.expander("April 2025: 💰 U.S. Liquid Money Supply vs S&P500", True):
    render_chart1_money_supply_vs_sp500()

    st.divider()
        
    render_chart2_tbill_vs_inflation()
        
with st.expander("🎲 Signals That Determine if the Market is Risk-On/Risk-Off"):
    render_chart1_hyg_tlt_vs_sp500()

# Footer
st.divider()
st.caption("Data sources: FRED (Federal Reserve Economic Data) | Yahoo Finance")
st.caption(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")