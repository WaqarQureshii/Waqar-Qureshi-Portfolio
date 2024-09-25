import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
from datetime import datetime
import sys
from functools import reduce

sys.path.append(".")
from functions.generation_equities import Generate_DB, Generate_DB_polars, filter_indices
from functions.generation_debt import Generate_Yield_panda

st.set_page_config(layout="wide",
                   page_title="What Transpired During Our Last Encounter (WTDOLLE)?",
                   initial_sidebar_state="collapsed")

st.title('What Transpired During Our Last Encounter (WTDOLLE)?')

# -------- DATE SELECTION SECTION --------
    # --- DATE SELECTION ---
today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
header_col1, header_col2, header_col3 = st.columns(3)
header_col1.info(icon="ℹ️", body='Select the time period you want to assess the equity market over (start date and end date)')
input_start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

    # --- INDEX PARAMETERS
header_col2.info(icon="ℹ️", body='Select the interval you\'d like to assess the market. All the figures and metrics will be assessed on the selected interval.')
selection_interval = header_col2.radio("Select Interval",
                                       options =['Daily', 'Weekly', 'Monthly'],
                                       index = 0,
                                       key = "interval_selection")

if selection_interval == 'Daily':
    input_interval = '1d'
    grammatical_selection = 'days'
elif selection_interval == 'Weekly':
    input_interval = '1wk'
    grammatical_selection = 'weeks'
elif selection_interval == 'Monthly':
    input_interval = '1mo'
    grammatical_selection = 'months'

header_col3.info(icon="ℹ️", body='This number will assess whether there was a positive return in X (selection) number of periods.')
input_returninterval = header_col3.number_input(f"Calculate return over # of {grammatical_selection}", min_value = 1, step=1, key="return interval selection")

# --- Dataframes Set Up ---
# ---------- DATAFRAMES FOR COMMON DATE INDICES --------------
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []
filtered_db_list=[] #to pass to filter_indices function

sidebar_counter = 0
st.subheader("")
st.info(icon="ℹ️", body='SELECT METRICS HERE TO GENERATE EQUITY MARKET GRAPHS AND EVENTS. Note: Equity market metrics are available in production currently. Debt Market and Economic Figures are currently in progress.')
inpcol1, inpcol2, inpcol3 = st.columns(3)
# EQUITY MARKET
equity_filters_applied_sentence = "Equity filters applied:"
equity_market = inpcol1.popover("Equity Market")
volatility_index_check = equity_market.checkbox("Volatility Index (VIX)", False)
equalweighted_sp500_check = equity_market.checkbox("Equal-Weighted S&P 500 (RSP)", False)
hyg_check = equity_market.checkbox("High-Yield Corporate Bonds (HYG)", False)
sp500_check = equity_market.checkbox("S&P 500 (GSPC)", False)
nasdaq_check = equity_market.checkbox("Nasdaq (IXIC)", False)
russell2000_check = equity_market.checkbox("Russell 2000 (RUT)", False)
equityratio_check = equity_market.checkbox("Ratio of 2 Equities", False)
# EQUITY MARKET -> VOLATILITY INDEX
if volatility_index_check:
    with inpcol1.expander("Volatility Index"):
        vix=Generate_DB_polars()
        vix.get_database(["^VIX"], input_start_date, input_end_date, input_interval)
        st.line_chart(vix.lf.select(["Date", "Close"]).collect(), x="Date", y="Close", height=200, use_container_width=True)

        vixcol1, vixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        vix_level_on = vixcol1.toggle("Price Level", key="vix p toggle")
        vix_pct_on = vixcol2.toggle("% Change", key="vix pct toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> VIX LEVEL
        if vix_level_on:
            vix_level_comparator = vixcol1.selectbox("VIX Comparator",('Greater than', 'Less than'))
            vix_level_selection = vixcol1.number_input("Select value", min_value=0.0, step=0.5)
            
            vix.metric_vs_selection_cross(comparison_type='current_price',selected_value=[vix_level_selection],comparator=vix_level_comparator)
            filtered_db_list.append(vix.filtered_dates)
            
            equity_filters_applied_sentence+=f" VIX level {vix_level_comparator} {vix_level_selection}"
            sidebar_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> VIX % CHANGE
        if vix_pct_on:
            vix_pct_lower = vixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            vix_pct_higher = vixcol2.number_input("Between higher value", step=0.6, key="vix between higher value")

            vix.metric_vs_selection_cross(comparison_type="% change between",selected_value=[vix_pct_lower, vix_pct_higher], comparator="Between")
            filtered_db_list.append(vix.filtered_dates)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" VIX % change between {vix_pct_lower}% and {vix_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", VIX % change between {vix_pct_lower}% and {vix_pct_higher}%"
            sidebar_counter+=1

# EQUITY MARKET -> RSP
if equalweighted_sp500_check:
    with inpcol1.expander("Equal-Weighted S&P"):
        rsp_chart_col1, rsp_chart_col2 = st.columns(2)
        rsp_rsi_length=rsp_chart_col1.number_input("Select RSI days", min_value=0, step=1, value=22, key="rsp rsi length selection")
        rsp_ma_length=rsp_chart_col2.number_input("Select MA days", min_value=0, step=1, value=50, key="rsp ma length selection")

        rsp = Generate_DB_polars()
        rsp.get_database('RSP', input_start_date, input_end_date, input_interval, rsi_value=rsp_rsi_length, ma_length=rsp_ma_length)

        st.line_chart(rsp.lf.select(["Date", "Close", "ma", "rsi"]).collect(), x="Date",y=["Close", "ma", "rsi"], height=200, use_container_width=True)

        rsp_col1, rsp_col2=st.columns(2)
    # EQUITY MARKET -> RSP -> RSP RSI / Moving Average / % Change
        rsp_rsi_on = rsp_col1.toggle("RSI", key="rsp rsi toggle")
        rsp_ma_on = rsp_col2.toggle("Moving Average", key="rsp ma toggle")
        # EQUITY MARKET -> RSP -> RSI
        if rsp_rsi_on:
            rsp_rsi_comparator = rsp_col1.selectbox("RSP comparator",('Greater than', 'Less than'))
            rsp_rsi_selection = rsp_col1.number_input("Select value", min_value=0.0, step=1.0, key="rsp rsi selection")

            rsp.metric_vs_selection_cross('current_price', [rsp_rsi_selection],rsp_rsi_comparator)
            filtered_db_list.append(rsp.filtered_dates)            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" RSP {rsp_rsi_length}-day RSI {rsp_rsi_comparator} {rsp_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", RSP {rsp_rsi_length}-day RSI {rsp_rsi_comparator} {rsp_rsi_selection}"
            sidebar_counter+=1
        # EQUITY MARKET -> RSP -> RSP Moving Average
        if rsp_ma_on:
            rsp_ma_comparator = rsp_col2.selectbox(f"RSP Price > or < {rsp_ma_length} day Moving Average", ('Greater than', 'Less than'))
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=rsp_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" RSP Price {rsp_ma_comparator} RSP {rsp_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", RSP Price {rsp_ma_comparator} RSP {rsp_ma_length} day Moving Average"
            sidebar_counter+=1
        
        # EQUITY MARKET -> RSP -> RSP RSI / Moving Average / % Change
        rsp_pct_on = rsp_col1.toggle("% Change", key="rsp % Change toggle")

        # EQUITY MARKET -> RSP -> % Change
        if rsp_pct_on:
            rsp_pct_lower = rsp_col1.number_input("Between lower value", step=0.5, key="rsp between lower value")
            rsp_pct_higher = rsp_col1.number_input("Between higher value", step=0.6, key="rsp between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[rsp_pct_lower, rsp_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" RSP % change between {rsp_pct_lower}% and {rsp_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", RSP % change between {rsp_pct_lower} and {rsp_pct_higher}%"
            sidebar_counter+=1

# EQUITY MARKET -> HYG
if hyg_check:
    with inpcol1.expander("High-Yield Corporate Bonds"):
        hyg_chart_col1, hyg_chart_col2 = st.columns(2)
        hyg_rsi_length=hyg_chart_col1.number_input("Select RSI days", min_value=0, step=1, value=22, key="hyg rsi length selection")
        hyg_ma_length=hyg_chart_col2.number_input("Select MA days", min_value=0, step=1, value=50, key="hyg ma length selection")

        hyg = Generate_DB()
        hyg.get_database('HYG', input_start_date, input_end_date, input_interval, rsi_value=hyg_rsi_length, ma_length=hyg_ma_length)
        hyg_linechart = hyg.db[['Close', 'ma', 'rsi']]
        st.line_chart(hyg_linechart, height=200, use_container_width=True)
        hyg_col1, hyg_col2=st.columns(2)
    # EQUITY MARKET -> HYG -> HYG RSI / Moving Average / % Change
        hyg_rsi_on = hyg_col1.toggle("RSI", key="hyg rsi toggle")
        hyg_ma_on = hyg_col2.toggle("Moving Average", key="hyg ma toggle")

        # EQUITY MARKET -> HYG -> RSI
        if hyg_rsi_on:
            hyg_rsi_comparator = hyg_col1.selectbox("HYG comparator",('Greater than', 'Less than'))
            hyg_rsi_selection = hyg_col1.number_input("Select value", min_value=0.0, step=1.0, key="hyg rsi selection")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_comparison_cross(comparison_type='rsi vs selection', comparator=hyg_rsi_comparator, selected_value=[hyg_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" HYG {hyg_rsi_length}-day RSI {hyg_rsi_comparator} {hyg_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", HYG {hyg_rsi_length}-day RSI {hyg_rsi_comparator} {hyg_rsi_selection}"
            sidebar_counter+=1
        # EQUITY MARKET -> HYG -> HYG Moving Average
        if hyg_ma_on:
            hyg_ma_comparator = hyg_col2.selectbox(f"HYG Price > or < {hyg_ma_length} day Moving Average", ('Greater than', 'Less than'))
            sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=hyg_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" HYG Price {hyg_ma_comparator} HYG {hyg_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", HYG Price {hyg_ma_comparator} HYG {hyg_ma_length} day Moving Average"
            sidebar_counter+=1
        
        # EQUITY MARKET -> HYG -> HYG RSI / Moving Average / % Change
        hyg_pct_on = hyg_col1.toggle("% Change", key="hyg % Change toggle")

        # EQUITY MARKET -> HYG -> % Change
        if hyg_pct_on:
            hyg_pct_lower = hyg_col1.number_input("Between lower value", step=0.5, key="hyg between lower value")
            hyg_pct_higher = hyg_col1.number_input("Between higher value", step=0.6, key="hyg between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[hyg_pct_lower, hyg_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" HYG % change between {hyg_pct_lower}% and {hyg_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", HYG % change between {hyg_pct_lower} and {hyg_pct_higher}%"
            sidebar_counter+=1

# EQUITY MARKET -> S&P 500
if sp500_check:
    with inpcol1.expander("S&P 500"):
        sp500_chartcol1, sp500_chartcol2 = st.columns(2)
        #EQUITY MARKET -> S&P500 -> RSI and MA selection & CHART
        sp500_rsi_length=sp500_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="S&P500 rsi length selection")
        sp500_ma_length=sp500_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="S&P500 ma length selection")
        sp500 = Generate_DB()
        sp500.get_database("^GSPC", start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=sp500_rsi_length, ma_length=sp500_ma_length)
        sp500_chart_p_ma, sp500_chart_rsi=sp500.db[['Close', 'ma']], sp500.db[['rsi']]
        sp500_chartcol1.line_chart(sp500_chart_rsi, height=200, use_container_width=True)
        sp500_chartcol2.line_chart(sp500_chart_p_ma, height=200, use_container_width=True)

        # EQUITY MARKET -> S&P 500 -> % CHANGE / Price vs MA / RSI
        sp500_col1,sp500_col2=st.columns(2)
        sp500_rsi_on = sp500_col1.toggle("RSI", key="sp500 RSI toggle")
        sp500_ma_on = sp500_col2.toggle("Moving Average", key="sp500 MA toggle")

        # EQUITY MARKET -> S&P 500 -> RSI
        if sp500_rsi_on:
            sp500_rsi_comparator = sp500_col1.selectbox("S&P comparator",('Greater than', 'Less than'))
            sp500_rsi_selection = sp500_col1.number_input("Select value", min_value=0.0, step=1.0, key="S&P rsi selection")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = sp500.metric_vs_comparison_cross(comparison_type='rsi vs selection', comparator=sp500_rsi_comparator, selected_value=[sp500_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" S&P500 Price {sp500_rsi_comparator} {sp500_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", S&P500 Price {sp500_rsi_comparator} {sp500_rsi_selection}"
            sidebar_counter+=1
        # EQUITY MARKET -> S&P 500 -> Moving Average
        if sp500_ma_on:
            sp500_ma_comparator = sp500_col2.selectbox(f"sp500 Price > or < {sp500_ma_length} day Moving Average", ('Greater than', 'Less than'))
            sp500_intersection, nasdaq_intersection, rus2k_intersection = sp500.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=sp500_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" S&P500 Price {sp500_ma_comparator} S&P500 {sp500_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", S&P500 Price {sp500_ma_comparator} S&P500 {sp500_ma_length} day Moving Average"
            sidebar_counter+=1
        
        # EQUITY MARKET -> S&P 500 -> % CHANGE / Price vs MA / RSI
        sp500_pct_on = sp500_col1.toggle("% Change", key="sp500 % Change toggle")

        # EQUITY MARKET -> S&P 500 -> % CHANGE
        if sp500_pct_on:
            sp500_pct_lower = sp500_col1.number_input("Between lower value", step=0.5, key="sp500 between lower value")
            sp500_pct_higher = sp500_col1.number_input("Between higher value", step=0.6, key="sp500 between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = sp500.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[sp500_pct_lower, sp500_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" S&P500 % change between {sp500_pct_lower}% and {sp500_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", S&P500 % change between {sp500_pct_lower}% and {sp500_pct_higher}%"
            sidebar_counter+=1
            
            sp500.db['% Change PCT'] = sp500.db['% Change']*100
            sp500_col2.line_chart(sp500.db[['% Change PCT']], height=200, use_container_width=True)

# EQUITY MARKET -> Nasdaq
if nasdaq_check:
    with inpcol1.expander("Nasdaq"):
        ndx_chartcol1, ndx_chartcol2 = st.columns(2)
        #EQUITY MARKET -> NASDAQ -> RSI and MA selection & CHART
        ndx_rsi_length=ndx_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="Nasdaq rsi length selection")
        ndx_ma_length=ndx_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="Nasdaq ma length selection")
        ndx = Generate_DB()
        ndx.get_database("^IXIC", start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=ndx_rsi_length, ma_length=ndx_ma_length)
        ndx_chart_p_ma, ndx_chart_rsi=ndx.db[['Close', 'ma']], ndx.db[['rsi']]
        ndx_chartcol1.line_chart(ndx_chart_rsi, height=200, use_container_width=True)
        ndx_chartcol2.line_chart(ndx_chart_p_ma, height=200, use_container_width=True)

        # EQUITY MARKET -> Nasdaq -> % CHANGE / Price vs MA / RSI
        ndx_col1,ndx_col2=st.columns(2)
        ndx_rsi_on = ndx_col1.toggle("RSI", key="ndx RSI toggle")
        ndx_ma_on = ndx_col2.toggle("Moving Average", key="ndx MA toggle")

        # EQUITY MARKET -> Nasdaq -> RSI
        if ndx_rsi_on:
            ndx_rsi_comparator = ndx_col1.selectbox("Nasdaq comparator",('Greater than', 'Less than'))
            ndx_rsi_selection = ndx_col1.number_input("Select value", min_value=0.0, step=1.0, key="Nasdaq rsi selection")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = ndx.metric_vs_comparison_cross(comparison_type='rsi vs selection', comparator=ndx_rsi_comparator, selected_value=[ndx_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq Price {ndx_rsi_comparator} {ndx_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", Nasdaq Price {ndx_rsi_comparator} {ndx_rsi_selection}"
            sidebar_counter+=1
        # EQUITY MARKET -> Nasdaq -> Moving Average
        if ndx_ma_on:
            ndx_ma_comparator = ndx_col2.selectbox(f"ndx Price > or < {ndx_ma_length} day Moving Average", ('Greater than', 'Less than'))
            sp500_intersection, nasdaq_intersection, rus2k_intersection = ndx.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=ndx_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq Price {ndx_ma_comparator} Nasdaq {ndx_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", Nasdaq Price {ndx_ma_comparator} Nasdaq {ndx_ma_length} day Moving Average"
            sidebar_counter+=1
        # EQUITY MARKET -> Nasdaq -> % CHANGE / Price vs MA / RSI
        ndx_pct_on = ndx_col1.toggle("% Change", key="ndx % Change toggle")

        # EQUITY MARKET -> Nasdaq -> % CHANGE
        if ndx_pct_on:
            ndx_pct_lower = ndx_col1.number_input("Between lower value", step=0.5, key="ndx between lower value")
            ndx_pct_higher = ndx_col1.number_input("Between higher value", step=0.6, key="ndx between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = ndx.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[ndx_pct_lower, ndx_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq % change between {ndx_pct_lower}% and {ndx_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", Nasdaq % change between {ndx_pct_lower}% and {ndx_pct_higher}%"
            sidebar_counter+=1

            ndx.db['% Change PCT'] = ndx.db['% Change']*100
            ndx_col2.line_chart(ndx.db[['% Change PCT']], height=200, use_container_width=True)

# EQUITY MARKET -> Russell 2000
if russell2000_check:
    with inpcol1.expander("Russell 2000"):
        rus2k_chartcol1, rus2k_chartcol2 = st.columns(2)
        #EQUITY MARKET -> Russell 2000 -> RSI and MA selection & CHART
        rus2k_rsi_length=rus2k_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="Russell 2000 rsi length selection")
        rus2k_ma_length=rus2k_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="Russell 2000 ma length selection")
        rus2k = Generate_DB()
        rus2k.get_database("^RUT", start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=rus2k_rsi_length, ma_length=rus2k_ma_length)
        rus2k_chart_p_ma, rus2k_chart_rsi=rus2k.db[['Close', 'ma']], rus2k.db[['rsi']]
        rus2k_chartcol1.line_chart(rus2k_chart_rsi, height=200, use_container_width=True)
        rus2k_chartcol2.line_chart(rus2k_chart_p_ma, height=200, use_container_width=True)

        # EQUITY MARKET -> Russell 2000 -> % CHANGE / Price vs MA / RSI
        rus2k_col1,rus2k_col2=st.columns(2)
        rus2k_rsi_on=rus2k_col1.toggle("RSI", key="rus2k RSI toggle")
        rus2k_ma_on=rus2k_col2.toggle("Moving Average", key="rus2k MA toggle")

        # EQUITY MARKET -> Russell 2000 -> RSI
        if rus2k_rsi_on:
            rus2k_rsi_comparator = rus2k_col1.selectbox("Russell 2000 comparator",('Greater than', 'Less than'))
            rus2k_rsi_selection = rus2k_col1.number_input("Select value", min_value=0.0, step=1.0, key="Russell 2000 rsi selection")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rus2k.metric_vs_comparison_cross(comparison_type='rsi vs selection', comparator=rus2k_rsi_comparator, selected_value=[rus2k_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 Price {rus2k_rsi_comparator} {rus2k_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 Price {rus2k_rsi_comparator} {rus2k_rsi_selection}"
            sidebar_counter+=1
        # EQUITY MARKET -> Nasdaq -> Moving Average
        if rus2k_ma_on:
            rus2k_ma_comparator = rus2k_col2.selectbox(f"rus2k Price > or < {rus2k_ma_length} day Moving Average", ('Greater than', 'Less than'))
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rus2k.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=rus2k_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 Price {rus2k_ma_comparator} Russell 2000 {rus2k_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 Price {rus2k_ma_comparator} Russell 2000 {rus2k_ma_length} day Moving Average"
            sidebar_counter+=1
        # EQUITY MARKET -> Russell 2000 -> % CHANGE / Price vs MA / RSI
        rus2k_pct_on = rus2k_col1.toggle("% Change", key="rus2k % Change toggle")

        # EQUITY MARKET -> Russell 2000 -> % CHANGE
        if rus2k_pct_on:
            rus2k_pct_lower = rus2k_col1.number_input("Between lower value", step=0.5, key="rus2k between lower value")
            rus2k_pct_higher = rus2k_col1.number_input("Between higher value", step=0.6, key="rus2k between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rus2k.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[rus2k_pct_lower, rus2k_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 % change between {rus2k_pct_lower}% and {rus2k_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 % change between {rus2k_pct_lower}% and {rus2k_pct_higher}%"
            sidebar_counter+=1

            rus2k.db['% Change PCT'] = rus2k.db['% Change']*100
            rus2k_col2.line_chart(rus2k.db[['% Change PCT']], height=200, use_container_width=True)

# EQUITY MARKET -> EQUTIY RATIO
if equityratio_check:
    with inpcol1.expander("Equity Ratio"):
        eq_ratio_col1, eq_ratio_col2 = st.columns(2)
        eq_ratio_numerator_selection = eq_ratio_col1.selectbox("Numerator", ("None", "Nasdaq", "S&P 500", "S&P 500 Equally Weighted", "Russell 2000"), key="equity ratio numerator selector")
        eq_ratio_denominator_selection = eq_ratio_col2.selectbox("Denominator", ("None", "Nasdaq", "S&P 500", "S&P 500 Equally Weighted", "Russell 2000"), key="equity ratio denominator selector")
        
        if not eq_ratio_numerator_selection == "None" and not eq_ratio_denominator_selection == "None":
            eq_ratio_rsi_length = eq_ratio_col1.number_input("Select RSI days", min_value=0, step=1, value=22, key="equity ratio RSI length")
            eq_ratio_ma_length = eq_ratio_col2.number_input("Select MA days", min_value=0, step=1, value=50, key="equity ratio MA length")
            equity_ratio = Generate_DB()
            equity_ratio.generate_ratio(eq_ratio_numerator_selection, eq_ratio_denominator_selection, input_start_date, input_end_date, input_interval, eq_ratio_rsi_length, eq_ratio_ma_length)
            equity_chart_ratio, equity_chart_ma_rsi = equity_ratio.db[["Close", "ma", "% Change"]], equity_ratio.db[["rsi"]]
            eq_ratio_col1.line_chart(equity_chart_ma_rsi, height=200, use_container_width=True)
            eq_ratio_col2.line_chart(equity_chart_ratio, height=200, use_container_width=True)

            # EQUITY MARKET -> EQUITY RATIO -> RSI / MA / % CHANGE
            eq_ratio_rsi_on = eq_ratio_col1.toggle("RSI", key="equity ratio RSI")
            eq_ratio_ma_on = eq_ratio_col2.toggle("MA", key="equity ratio MA")

            # EQUITY MARKET -> EQUITY RATIO -> RSI
            if eq_ratio_rsi_on:
                eq_ratio_comparator = eq_ratio_col1.selectbox("Ratio comparator", ("Greater than", "Less than"), key="equity ratio comparator")
                eq_ratio_rsi_selection = eq_ratio_col2.number_input("Select RSI value", min_value=0.0, step=1.0, key="equity ratio RSI selection")
                sp500_intersection, nasdaq_intersection, rus2k_intersection = equity_ratio.metric_vs_comparison_cross(comparison_type="rsi vs selection", comparator=eq_ratio_comparator, selected_value=[eq_ratio_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
                
                if sidebar_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio Price {eq_ratio_comparator} {eq_ratio_rsi_selection}"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio Price {eq_ratio_comparator} {eq_ratio_rsi_selection}"
                sidebar_counter+=1
            
            # EQUITY MARKET -> EQUITY RATIO -> MA
            if eq_ratio_ma_on:
                eq_ratio_ma_comparator = eq_ratio_col2.selectbox(f"Equity Ratio > or < {eq_ratio_ma_length} day Moving Average", ('Greater than','Less than'))
                sp500_intersection, nasdaq_intersection, rus2k_intersection = equity_ratio.metric_vs_comparison_cross(comparison_type='price vs ma', selected_value=(), comparator=eq_ratio_ma_comparator, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
                
                if sidebar_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio Price {eq_ratio_ma_comparator} Equity Ratio {eq_ratio_ma_length} day Moving Average"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio Price {eq_ratio_ma_comparator} Equity Ratio {eq_ratio_ma_length} day Moving Average"
                sidebar_counter+=1
            
            # EQUITY MARKET -> EQUITY RATIO -> % CHANGE
            eq_ratio_pct_on=eq_ratio_col1.toggle("% Change", key="equity ratio % change")

            # EQUITY MARKET -> EQUITY RATIO -> % CHANGE
            if eq_ratio_pct_on:
                eqratio_pct_lower = eq_ratio_col1.number_input("Between lower value", step=0.5, key="equity ratio between lower value")
                eqratio_pct_higher = eq_ratio_col1.number_input("Between higher value", step=0.6, key="equity ratio between higher value")
                sp500_intersection, nasdaq_intersection, rus2k_intersection = equity_ratio.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[eqratio_pct_lower, eqratio_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

                if sidebar_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio % change between {eqratio_pct_lower}% and {eqratio_pct_higher}%"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio % change between {eqratio_pct_lower}% and {eqratio_pct_higher}%"
                sidebar_counter+=1

# EQUITY MARKET -> SUMMARY
inpcol1.write("*"+equity_filters_applied_sentence+"*")

# DEBT MARKET
debt_filters_applied_sentence = "Debt filters applied:"
debt_market = inpcol2.popover("Debt Market")
yieldspread_check = debt_market.checkbox("Market Yield Spread (Yield Curve)", False)
usfedfundrate_check = debt_market.checkbox("US Federal Funds Rate", False)


# DEBT MARKET -> YIELD SPREAD
if yieldspread_check:
    with inpcol2.expander("Yield Spread"):
        yieldspread = Generate_Yield_panda()
        spreadcol1, spreadcol2 = st.columns(2)

        # DEBT MARKET -> YIELD SPREAD -> Long Term
        lt_maturity_selection = spreadcol1.selectbox("Long-Term Maturity", ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"), index=8)

        # DEBT MARKET -> YIELD SPREAD -> Short Term
        st_maturity_selection = spreadcol2.selectbox("Short-Term Maturity", ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"), index=4)

        # DEBT MARKET -> YIELD SPREAD
        yieldspread.generate_yield_spread(input_start_date, input_end_date, selection_interval, lt_maturity_selection, st_maturity_selection)
        spread_linechart = yieldspread.yielddiff_df[[f'{lt_maturity_selection} Rate', f'{st_maturity_selection} Rate', 'Rate Spread', '% Change']]
        spreadcol1.line_chart(spread_linechart, height=200, use_container_width=True, y=[f'{lt_maturity_selection} Rate', f'{st_maturity_selection} Rate', 'Rate Spread'], color=['#c9c9e6', '#cce6c9', '#be2a25'])
        spreadcol2.dataframe(spread_linechart, height=207, column_order=['Rate Spread', '% Change'],column_config={
            "": st.column_config.DatetimeColumn(
                "Date",
                format="YYYY-MM-DD"
            ),
            '% Change': st.column_config.NumberColumn(
                "% Change",
                format="%.2f%%"
            )
        })

        spread_level_on=spreadcol1.toggle("Spread Level", key="spread level toggle")
        spread_pct_on=spreadcol2.toggle("Spread % Change", key="spread %chg toggle")
        
        # DEBT MARKET -> YIELD SPREAD -> SPREAD LEVEL
        if spread_level_on:
            spread_level_comparator = spreadcol1.selectbox("Spread Comparator", ('Greater than', 'Less than'))
            spread_level_selection=spreadcol1.number_input("Select value", step=1.0, value=0.0)
            sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldspread.metric_vs_selection(movement='cross',comparison_type='current price', comparator=spread_level_comparator, selected_value=[spread_level_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            debt_filters_applied_sentence+=f" Spread Level {spread_level_comparator} {spread_level_selection}"
            sidebar_counter+=1
        
        if spread_pct_on:
            spread_pct_lower = spreadcol2.number_input("Between lower value", step=0.5, key="spread between lower value")
            spread_pct_higher = spreadcol2.number_input("Between higher value", step=0.5, key="spread between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldspread.metric_vs_selection(movement='cross', comparison_type='% change between', comparator="Between", selected_value=[spread_pct_lower, spread_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                debt_filters_applied_sentence+=f" Spread % change between {spread_pct_lower}% and {spread_pct_higher}%"
            else:
                debt_filters_applied_sentence+=f", Spread % change between {spread_pct_lower}% and {spread_pct_higher}%"
            sidebar_counter+=1

if usfedfundrate_check:    
    with inpcol2.expander("US Federal Funds Rate"):
        usfedfund = Generate_Yield_panda()
        usfedfund.get_database("US FED FUNDS", input_start_date, input_end_date, selection_interval)
        
        usfedr_col1, usdfedr_col2 = st.columns(2)

        # DEBT MARKET -> US FED FUND RATE -> Change
        usfedr_col1.line_chart(usfedfund.df, y=['US FED FUNDS Rate'], height=200)
        
        usfedrate_level_on = usdfedr_col2.toggle("US Fed Funds Rate Change", key="US Fed Funds Rate Change")

        if usfedrate_level_on:
            usfedrate_level_selection_lower = usdfedr_col2.number_input("Increase/Decrease Between (lower value)", step=0.25, value=-0.30)
            usfedrate_level_selection_higher = usdfedr_col2.number_input("Increase/Decrease Between (higher value)", step=0.25, value=-0.20)
            sp500_intersection, nasdaq_intersection, rus2k_intersection = usfedfund.metric_vs_selection(movement='cross', comparison_type='change between', comparator="change between", selected_value=[usfedrate_level_selection_lower, usfedrate_level_selection_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            if sidebar_counter==0:
                debt_filters_applied_sentence+=f" US Fed Funds Rate change between {usfedrate_level_selection_lower}% and {usfedrate_level_selection_higher}%"
            else:
                debt_filters_applied_sentence+=f", US Fed Funds Rate change between {usfedrate_level_selection_lower}% and {usfedrate_level_selection_higher}%"
            sidebar_counter+=1

# DEBT MARKET -> SUMMARY
inpcol2.write("*"+debt_filters_applied_sentence+"*")

inpcol3.subheader("Economic Figures - IN PROGRESS")


# --- SELECTED VARIABLES COLUMNS ---
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)


# --- MAIN PAGE OF WTDOLLE - CHARTS AND PARAMETERS
    # -------------------- HEADER -------------------------
st.header(f'WTDOLLE on {input_end_date}')

# ---------MODIFYING THE METRIC FORMAT ------------------
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

#--- PLOTTING GRAPH ---
col1, col2, col3 = st.columns(3)
graph1, graph2, graph3= st.columns(3)

#-------INDICES PARAMETER SELECTION-------
col1.subheader("S&P 500")

col2.subheader("Nasdaq")

col3.subheader("Russell 2000")

# --- Indices Generation ---
if sidebar_counter > 0:
    #---S&P500 DATABASE GENERATION---
    if 'sp500' not in globals():
        sp500 = Generate_DB()
        sp500.get_database("^GSPC", input_start_date, input_end_date, input_interval)
    sp500.generate_common_dates(sp500_intersection,selected_returninterval=input_returninterval)
    #-------S&P500 GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('S&P500')
    ax.plot(sp500.db.index, sp500.db['Close'], linewidth = 0.5, color='black')
    try:
        ax.scatter(sp500.common_dates.index, sp500.common_dates['Close'], marker='.', color='red', s = 10)
        graph1.pyplot(fig)
        #-------S&P500 GENERATE STATEMENTS--------
        graph1.write(f'This occurred {sp500.no_of_occurrences} of time(s) and is {sp500.positive_percentage} positive in {input_returninterval} days.' )
        graph1.write('{:.2%}'.format(sp500.avg_return))
    except AttributeError:
        graph1.write("There are no scenarios that exist like this.")

    #---NASDAQ DATABASE GENERATION---
    if 'ndx' not in globals():
        ndx = Generate_DB()
        ndx.get_database("^IXIC", input_start_date, input_end_date, input_interval)
    ndx.generate_common_dates(nasdaq_intersection, selected_returninterval=input_returninterval)
    #-------NASDAQ GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('Nasdaq 100')
    try:
        ax.plot(ndx.db.index, ndx.db['Close'], linewidth = 0.5, color='black')
        ax.scatter(ndx.common_dates.index, ndx.common_dates['Close'], marker='.', color='red', s = 10)
        graph2.pyplot(fig)
        #-------NASDAQ GENERATE STATEMENTS-------
        graph2.write(f'This occurred {ndx.no_of_occurrences} time(s) and is {ndx.positive_percentage} positive in {input_returninterval} days.' )
        graph2.write('{:.2%}'.format(ndx.avg_return))
    except AttributeError:
        graph2.write("There are no scenarios that exist like this.")
    
    #--RUSSEL 2000 DATABASE GENERATION
    if 'rus2k' not in globals():
        rus2k = Generate_DB()
        rus2k.get_database("^RUT", input_start_date, input_end_date, input_interval)
    rus2k.generate_common_dates(rus2k_intersection, selected_returninterval=input_returninterval)
    #-----RUSSELL 2000 GRAPH-----
    fig, ax = plt.subplots()
    ax.set_title('Russel 2000')
    try:
        ax.plot(rus2k.db.index, rus2k.db['Close'], linewidth = 0.5, color='black')
        ax.scatter(rus2k.common_dates.index, rus2k.common_dates['Close'], marker='.', color='red', s = 10)
        graph3.pyplot(fig)
        #-------NASDAQ GENERATE STATEMENTS-------
        graph3.write(f'This occurred {rus2k.no_of_occurrences} of time(s) and is {rus2k.positive_percentage} positive in {input_returninterval} days.' )
        graph3.write('{:.2%}'.format(rus2k.avg_return))
    except AttributeError:
        graph3.write("There are no scenarios that exist like this.")

else:
    pass