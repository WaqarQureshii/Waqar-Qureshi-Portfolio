import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
from datetime import datetime
import sys
from functools import reduce

sys.path.append(".")
from functions.generate_db import *
from functions.signal_generators import *
from functions.generations import Generate_DB, Generate_Yield

st.set_page_config(layout="wide")

st.title('What Transpired During Our Last Encounter (WTDOLLE)?')

# -------- DATE SELECTION SECTION --------
    # --- DATE SELECTION ---
today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
header_col1, header_col2, header_col3 = st.columns(3)
input_start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

    # --- INDEX PARAMETERS
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

input_returninterval = header_col3.number_input(f"Calculate over # of {grammatical_selection}", min_value = 1, step=1, key="return interval selection") #TODO need to link to Indices graph input, after deprecating existing individual selection.

# --- Dataframes Set Up ---
# ---------- DATAFRAMES FOR COMMON DATE INDICES --------------
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []

sidebar_counter = 0

inpcol1, inpcol2, inpcol3 = st.columns(3)
# EQUITY MARKET
equity_filters_applied_sentence = "Equity filters applied:"
equity_market = inpcol1.popover("Equity Market")
volatility_index_check = equity_market.checkbox("Volatility Index (VIX)", False)
equalweighted_sp500_check = equity_market.checkbox("Equal-Weighted S&P 500 (RSP)", False)
sp500_check = equity_market.checkbox("S&P 500 (GSPC)", False)
nasdaq_check = equity_market.checkbox("Nasdaq (IXIC)", False)
russell2000_check = equity_market.checkbox("Russell 2000 (RUT)", False)
equityratio_check = equity_market.checkbox("Ratio of 2 Equities", False)
# EQUITY MARKET -> VOLATILITY INDEX
if volatility_index_check:
    with inpcol1.expander("Volatility Index"):
        vix = Generate_DB()
        vix.get_database('^VIX', input_start_date, input_end_date, input_interval)
        vix_line_chart = vix.db[['% Change', 'Close']]
        vix_line_chart['% Change'] = vix_line_chart['% Change'] * 100
        st.line_chart(vix_line_chart, height=200, use_container_width=True)
        vixcol1, vixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        vix_level_on = vixcol1.toggle("Price Level", key="vix p toggle")
        vix_pct_on = vixcol2.toggle("% Change", key="vix pct toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> VIX LEVEL
        if vix_level_on:
            vix_level_comparator = vixcol1.selectbox("VIX Comparator",('Greater than', 'Less than'))
            vix_level_selection = vixcol1.number_input("Select value", min_value=0.0, step=0.5)
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_comparison_cross(comparison_type='current price', comparator=vix_level_comparator, selected_value=[vix_level_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            equity_filters_applied_sentence+=f" VIX level {vix_level_comparator} {vix_level_selection}"
            sidebar_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> VIX % CHANGE
        if vix_pct_on:
            vix_pct_lower = vixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            vix_pct_higher = vixcol2.number_input("Between higher value", step=0.6, key="vix between higher value")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_comparison_cross(comparison_type='% change between', comparator="Between", selected_value=[vix_pct_lower, vix_pct_higher], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
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

        rsp = Generate_DB()
        rsp.get_database('RSP', input_start_date, input_end_date, input_interval, rsi_value=rsp_rsi_length, ma_length=rsp_ma_length)
        rsp_linechart = rsp.db[['Close', 'ma', 'rsi']]
        st.line_chart(rsp_linechart, height=200, use_container_width=True)
        rsp_col1, rsp_col2=st.columns(2)
    # EQUITY MARKET -> RSP -> RSP RSI / Moving Average / % Change
        rsp_rsi_on = rsp_col1.toggle("RSI", key="rsp rsi toggle")
        rsp_ma_on = rsp_col2.toggle("Moving Average", key="rsp ma toggle")

        # EQUITY MARKET -> RSP -> RSI
        if rsp_rsi_on:
            rsp_rsi_comparator = rsp_col1.selectbox("RSP comparator",('Greater than', 'Less than'))
            rsp_rsi_selection = rsp_col1.number_input("Select value", min_value=0.0, step=1.0, key="rsp rsi selection")
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_comparison_cross(comparison_type='rsi vs selection', comparator=rsp_rsi_comparator, selected_value=[rsp_rsi_selection], sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)
            
            if sidebar_counter==0:
                equity_filters_applied_sentence+=f" RSP Price {rsp_rsi_comparator} {rsp_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", RSP Price {rsp_rsi_comparator} {rsp_rsi_selection}"
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

inpcol1.write("*"+equity_filters_applied_sentence+"*")


inpcol2.subheader("Debt Market")

inpcol3.subheader("Economic Figures")

#Creating the sidebar with the different signal creations
st.sidebar.subheader("Global Parameters used with WTDOLLE")


# --- SELECTED VARIABLES COLUMNS ---
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

# ------- SIDEBAR SELECTIONS ---------
st.sidebar.divider()

    # --- HYG OPTIONS ---
header_show_hyg = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=False)
if header_show_hyg == True:
    sidebar_counter += 1
    hyg = Generate_DB()
    hyg.get_database('HYG', input_start_date, input_end_date, input_interval)

    subheader_comparator_hyg = st.sidebar.radio('Choose HYG comparator',
    ['Greater than', "Less than"],
    index = 1, key = "comparator hyg pct selector")
    selected_pct_change = float(st.sidebar.text_input("Input percent increase/decrease", value = 
    hyg.pctchg_ceil_int*100, key = 'HYG pct comparator value'))
    
    if subheader_comparator_hyg == 'Greater than':
        ndx_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_selection('% change', subheader_comparator_hyg, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        
        col2.metric(label = f"HYG % > {selected_pct_change}", value = f'{hyg.boolean_comp} @ {hyg.pctchg_str}')
    else:
        sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_selection('% change', subheader_comparator_hyg, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        
        col2.metric(label = f"HYG % < {selected_pct_change}", value = f'{hyg.boolean_comp} @ {hyg.pctchg_str}')
    
    col2.line_chart(hyg.db['% Change']*100, height = 100, use_container_width = True)

st.sidebar.divider()

    # --- YIELD CURVE ---
show_yieldratio = st.sidebar.checkbox("US Yield Ratio", value=False, key='show yield ratio')
if show_yieldratio == True:
    yield_dict = {
        "30-year": '^TYX',
        "10-year": '^TNX'
    }
    sidebar_counter += 1
    show_yield_option = st.sidebar.radio('3 month vs',
                                    ['10-year',
                                    '30-year'],
                                    index = 1,
                                    key = 'show yield option')
    yieldcurve_comparator_selection = st.sidebar.radio('Choose Yield Curve comparator',
                                ['Diff greater than', 'Diff less than'],
                                index = 0)
    selected_yieldratio = float(st.sidebar.text_input("Input Yield Ratio to compare",
                                                 0.5,
                                                 key = 'Yield Curve level'))
    
    if show_yield_option == '30-year':
        yieldratio = Generate_Yield()
        yieldratio.generate_yield_ratio(start_date=input_start_date, end_date=input_end_date, interval=input_interval, numerator='^IRX', denominator=yield_dict[show_yield_option]) #TODO pull from FRED data instead.
        
        if yieldcurve_comparator_selection == "Diff greater than": # Current Yield Curve greater than Selected Difference Value
            sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldratio.metric_vs_selection(comparison_type='ratio vs selection', comparator='Greater than', selected_value=selected_yieldratio,sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            col5.metric(label=f'Yield Diff > {selected_yieldratio}', value = f'{yieldratio.boolean_comp} @ {yieldratio.curr_yieldratio}')
        
        else: # Current Yield Curve less than Selected Difference Value
            sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldratio.metric_vs_selection(comparison_type='ratio vs selection', comparator='Less than', selected_value=selected_yieldratio,sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            col5.metric(label=f'Yield Diff < {selected_yieldratio}', value = f'{yieldratio.boolean_comp} @ {yieldratio.curr_yieldratio}')

    col5.line_chart(yieldratio.yield_ratio['Yield Ratio'],
                    use_container_width = True,
                    height = 100)

st.sidebar.divider()    

# show_consumer = st.sidebar.checkbox("Consumer Index - XLY")
# if show_consumer == True:
#         sidebar_counter += 1

# show_utility = st.sidebar.checkbox("Utility (safe investment index) XLU")
# if show_utility == True:
#         sidebar_counter += 1

#TODO Implement Index Ratio parameter
# show_ndxVSsp = st.sidebar.checkbox("Nasdaq vs S&P500 ratio", value=True)
# if show_ndxVSsp == True:
#         sidebar_counter += 1


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
with col1.expander("S&P500 Parameter Selection"):
    sp500col1, sp500col2 = st.columns(2)
    with sp500col1:
        sp500_return_interval = int(st.text_input(f"# of {grammatical_selection} to calculate return over", 10, key="sp500 return interval"))
    with sp500col2:
        sp500rsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='sp500 RSI show')
        if sp500rsishow:
            sp500_rsi_length = int(st.text_input('Select RSI length (in intervals)', 22, key = "sp500 RSI length"))
            sp500 = Generate_DB()
            sp500.get_database('^GSPC', input_start_date, input_end_date, input_interval, sp500_rsi_length)
            sp500comparator = st.radio(f'Choose comparator, current RSI {sp500.curr_rsi}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="sp500 RSI comparator")
            sp500rsivalue = int(st.text_input('Input RSI value',
                                              sp500.curr_rsi - 1,
                                              key="sp500rsivalue"))

            if sp500comparator == 'Greater than':
                filtered_sp500rsi_metric = sp500.db[sp500.db['rsi'] > sp500rsivalue]
                sp500_intersection.append(filtered_sp500rsi_metric)
            else:
                filtered_sp500rsi_metric = sp500.db[sp500.db['rsi'] < sp500rsivalue]
                sp500_intersection.append(filtered_sp500rsi_metric)
        else:
            sp500 = Generate_DB()
            sp500.get_database('^GSPC', input_start_date, input_end_date, input_interval)

col2.subheader("Nasdaq")
with col2.expander("Nasdaq Parameter Section"):
    ndxcol1, ndxcol2 = st.columns(2)
    with ndxcol1:
        ndx_return_interval = int(st.text_input(f"# of {grammatical_selection} to calculate return over", 10, key="ndx return interval"))
    with ndxcol2:
        ndxrsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='ndx RSI show')
        if ndxrsishow:
            ndx_rsi_length = int(st.text_input('Select RSI length (in intervals)', 22, key = "ndx RSI length"))
            ndx = Generate_DB()
            ndx.get_database('^IXIC', input_start_date, input_end_date, input_interval, ndx_rsi_length)
            ndxcomparator = st.radio(f'Choose comparator, current RSI {ndx.curr_rsi}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="ndx RSI comparator")
            ndxrsivalue = int(st.text_input('Input RSI value',
                                            ndx.curr_rsi - 1,
                                            key="ndxrsivalue"))
            
            if ndxcomparator =='Greater than':
                filtered_ndxrsi_metric = ndx.db[ndx.db['rsi'] > ndxrsivalue]
                nasdaq_intersection.append(filtered_ndxrsi_metric)
            else:
                filtered_ndxrsi_metric = ndx.db[ndx.db['rsi'] < ndxrsivalue]
                nasdaq_intersection.append(filtered_ndxrsi_metric)
        else:
            ndx = Generate_DB()
            ndx.get_database('^IXIC', input_start_date, input_end_date, input_interval)

col3.subheader("Russell 2000")
with col3.expander("Russell 2000 Parameter Section"):
    rus2kcol1, rus2kcol2 = st.columns(2)
    with rus2kcol1:
        rus2k_return_interval = int(st.text_input(f"# of {grammatical_selection} to calculate return over", 10, key="rus2k return interval"))
    with rus2kcol2:
        rus2krsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='rus2k RSI show')
        if rus2krsishow:
            rus2k_rsi_length = int(st.text_input('Select RSI lenght (in intervals)', 22, key = "rus2k RSI length"))
            rus2k = Generate_DB()
            rus2k.get_database('^RUT', input_start_date, input_end_date, input_interval, rus2k_rsi_length)
            rus2kcomparator = st.radio(f'Choose comparator, current RSI {rus2k.curr_rsi}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="rus2k RSI comparator")
            rus2krsivalue = int(st.text_input('Input RSI value',
                                            rus2k.curr_rsi - 1,
                                            key='rus2krsivalue'))
            
            if rus2kcomparator == 'Greater than':
                filtered_rus2krsi_metric = rus2k.db[rus2k.db['rsi'] > rus2krsivalue]
                rus2k_intersection.append(filtered_rus2krsi_metric)

            else:
                filtered_rus2krsi_metric = rus2k.db[rus2k.db['rsi'] < rus2krsivalue]
                rus2k_intersection.append(filtered_rus2krsi_metric)
        else:
            rus2k = Generate_DB()
            rus2k.get_database('^RUT', input_start_date, input_end_date, input_interval)

# --- Indices Generation ---
if sidebar_counter > 0:
    #---S&P500 DATABASE GENERATION---
    db_filtered_sp500, avg_sp500_return, no_of_occurrences_sp500, positive_percentage_sp500 = signal_pct_positive(sp500.db, sp500_intersection, sp500_return_interval)
    #-------S&P500 GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('S&P500')
    ax.plot(sp500.db.index, sp500.db['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_sp500.index, db_filtered_sp500['Close'], marker='.', color='red', s = 10)
    graph1.pyplot(fig)
    #-------S&P500 GENERATE STATEMENTS--------
    graph1.write(f'This occurred {no_of_occurrences_sp500} of time(s) and is {positive_percentage_sp500} positive in {sp500_return_interval} days.' )
    graph1.write('{:.2%}'.format(avg_sp500_return))

    #---NASDAQ DATABASE GENERATION---
    db_filtered_ndx, avg_ndx_return, no_of_occurrences_ndx, positive_percentage_ndx = signal_pct_positive(ndx.db, nasdaq_intersection, ndx_return_interval)
    #-------NASDAQ GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('Nasdaq 100')
    ax.plot(ndx.db.index, ndx.db['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_ndx.index, db_filtered_ndx['Close'], marker='.', color='red', s = 10)
    graph2.pyplot(fig)
    #-------NASDAQ GENERATE STATEMENTS-------
    graph2.write(f'This occurred {no_of_occurrences_ndx} time(s) and is {positive_percentage_ndx} positive in {ndx_return_interval} days.' )
    graph2.write('{:.2%}'.format(avg_ndx_return))

    #--RUSSEL 2000 DATABASE GENERATION
    db_filtered_rus2k, avg_rus2k_return, no_of_occurrences_rus2k, positive_percentage_rus2k = signal_pct_positive(rus2k.db, rus2k_intersection, rus2k_return_interval)
    #-----RUSSELL 2000 GRAPH-----
    fig, ax = plt.subplots()
    ax.set_title('Russel 2000')
    ax.plot(rus2k.db.index, rus2k.db['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_rus2k.index, db_filtered_rus2k['Close'], marker='.', color='red', s = 10)
    graph3.pyplot(fig)
    #-------NASDAQ GENERATE STATEMENTS-------
    graph3.write(f'This occurred {no_of_occurrences_rus2k} of time(s) and is {positive_percentage_rus2k} positive in {rus2k_return_interval} days.' )
    graph3.write('{:.2%}'.format(avg_rus2k_return))

else:
    pass