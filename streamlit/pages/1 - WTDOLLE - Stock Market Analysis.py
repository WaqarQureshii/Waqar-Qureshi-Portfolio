import streamlit as st
import matplotlib.pyplot as plt

from datetime import datetime
from functools import reduce
import sys
sys.path.append(".")

from functions.generate_databases import Generate_Equity, Generate_Debt, Generate_Indicator, filter_indices
from functions.graphing_results import apply_filters

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
input_returninterval = header_col3.number_input(f"Calculate return over # of {grammatical_selection}", min_value = 1, step=1, key="return interval selection", value=30)

# --- Dataframes Set Up ---
# ---------- DATAFRAMES FOR COMMON DATE INDICES --------------
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []
filtered_db_list=[] #to pass to filter_indices function

equity_counter = 0
st.subheader("")
st.info(icon="ℹ️", body='SELECT METRICS HERE TO GENERATE EQUITY MARKET GRAPHS AND EVENTS. Note: Equity market metrics, Debt Market metrics, and Economic/Statistical metrics are available in production currently.')
inpcol1, inpcol2, inpcol3 = st.columns(3)
# EQUITY MARKET
equity_filters_applied_sentence = "Equity filters to apply:"
equity_market = inpcol1.popover("Equity Market")
equalweighted_sp500_check = equity_market.checkbox("Equal-Weighted S&P 500 (RSP)", False)
hyg_check = equity_market.checkbox("High-Yield Corporate Bonds (HYG)", False)
sp500_check = equity_market.checkbox("S&P 500 (GSPC)", False)
nasdaq_check = equity_market.checkbox("Nasdaq (IXIC)", False)
russell2000_check = equity_market.checkbox("Russell 2000 (RUT)", False)
equityratio_check = equity_market.checkbox("Ratio of 2 Equities", False)


# EQUITY MARKET -> RSP
if equalweighted_sp500_check:
    with inpcol1.expander("Equal-Weighted S&P"):
        rsp_chart_col1, rsp_chart_col2 = st.columns(2)
        rsp_rsi_length=rsp_chart_col1.number_input("Select RSI days", min_value=1, step=1, value=22, key="rsp rsi length selection")
        rsp_ma_length=rsp_chart_col2.number_input("Select MA days", min_value=1, step=1, value=50, key="rsp ma length selection")

        rsp = Generate_Equity()
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

            rsp.metric_vs_selection_cross('rsi_vs_selection', [rsp_rsi_selection], rsp_rsi_comparator)
            filtered_db_list.append(rsp.filtered_dates)
            
            if equity_counter==0:
                equity_filters_applied_sentence+=f" RSP {rsp_rsi_length}-day RSI {rsp_rsi_comparator} {rsp_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", RSP {rsp_rsi_length}-day RSI {rsp_rsi_comparator} {rsp_rsi_selection}"
            equity_counter+=1
        # EQUITY MARKET -> RSP -> RSP Moving Average
        if rsp_ma_on:
            rsp_ma_comparator = rsp_col2.selectbox(f"RSP Price > or < {rsp_ma_length} day Moving Average", ('Greater than', 'Less than'))
            
            rsp.metric_vs_selection_cross('price_vs_ma', rsp_ma_comparator)
            filtered_db_list.append(rsp.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" RSP Price {rsp_ma_comparator} RSP {rsp_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", RSP Price {rsp_ma_comparator} RSP {rsp_ma_length} day Moving Average"
            equity_counter+=1
        
        # EQUITY MARKET -> RSP -> RSP RSI / Moving Average / % Change
        rsp_pct_on = rsp_col1.toggle("% Change", key="rsp % Change toggle")

        # EQUITY MARKET -> RSP -> % Change
        if rsp_pct_on:
            rsp_pct_lower = rsp_col1.number_input("Between lower value", step=0.5, key="rsp between lower value")
            rsp_pct_higher = rsp_col1.number_input("Between higher value", step=0.6, key="rsp between higher value")

            rsp.metric_vs_selection_cross("%_change","Between", [rsp_pct_lower, rsp_pct_higher])
            filtered_db_list.append(rsp.filtered_dates)
            
            if equity_counter==0:
                equity_filters_applied_sentence+=f" RSP % change between {rsp_pct_lower}% and {rsp_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", RSP % change between {rsp_pct_lower} and {rsp_pct_higher}%"
            equity_counter+=1

# EQUITY MARKET -> HYG
if hyg_check:
    with inpcol1.expander("High-Yield Corporate Bonds"):
        hyg_chart_col1, hyg_chart_col2 = st.columns(2)
        hyg_rsi_length=hyg_chart_col1.number_input("Select RSI days", min_value=0, step=1, value=22, key="hyg rsi length selection")
        hyg_ma_length=hyg_chart_col2.number_input("Select MA days", min_value=0, step=1, value=50, key="hyg ma length selection")

        hyg = Generate_Equity()
        hyg.get_database(['HYG'], input_start_date, input_end_date, input_interval, rsi_value=hyg_rsi_length, ma_length=hyg_ma_length)
        st.line_chart(hyg.lf.select(["Date", "Close", "ma", "rsi"]).collect(),x="Date",y=["Close", "ma", "rsi"], height=200, use_container_width=True)

        hyg_col1, hyg_col2=st.columns(2)
    # EQUITY MARKET -> HYG -> HYG RSI / Moving Average / % Change
        hyg_rsi_on = hyg_col1.toggle("RSI", key="hyg rsi toggle")
        hyg_ma_on = hyg_col2.toggle("Moving Average", key="hyg ma toggle")

        # EQUITY MARKET -> HYG -> RSI
        if hyg_rsi_on:
            hyg_rsi_comparator = hyg_col1.selectbox("HYG comparator",('Greater than', 'Less than'))
            hyg_rsi_selection = hyg_col1.number_input("Select value", min_value=0.0, step=1.0, key="hyg rsi selection")

            hyg.metric_vs_selection_cross("rsi_vs_selection", hyg_rsi_comparator, [hyg_rsi_selection])
            filtered_db_list.append(hyg.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" HYG {hyg_rsi_length}-day RSI {hyg_rsi_comparator} {hyg_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", HYG {hyg_rsi_length}-day RSI {hyg_rsi_comparator} {hyg_rsi_selection}"
            equity_counter+=1
        # EQUITY MARKET -> HYG -> HYG Moving Average
        if hyg_ma_on:
            hyg_ma_comparator = hyg_col2.selectbox(f"HYG Price > or < {hyg_ma_length} day Moving Average", ('Greater than', 'Less than'))
            
            hyg.metric_vs_selection_cross("price_vs_ma", hyg_ma_comparator)
            filtered_db_list.append(hyg.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" HYG Price {hyg_ma_comparator} HYG {hyg_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", HYG Price {hyg_ma_comparator} HYG {hyg_ma_length} day Moving Average"
            equity_counter+=1
        
        # EQUITY MARKET -> HYG -> HYG RSI / Moving Average / % Change
        hyg_pct_on = hyg_col1.toggle("% Change", key="hyg % Change toggle")

        # EQUITY MARKET -> HYG -> % Change
        if hyg_pct_on:
            hyg_pct_lower = hyg_col1.number_input("Between lower value", step=0.5, key="hyg between lower value")
            hyg_pct_higher = hyg_col1.number_input("Between higher value", step=0.6, key="hyg between higher value")
            
            hyg.metric_vs_selection_cross("%_change", "Between", [hyg_pct_lower, hyg_pct_higher])
            filtered_db_list.append(hyg.filtered_dates)
            
            if equity_counter==0:
                equity_filters_applied_sentence+=f" HYG % change between {hyg_pct_lower}% and {hyg_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", HYG % change between {hyg_pct_lower} and {hyg_pct_higher}%"
            equity_counter+=1

# EQUITY MARKET -> S&P 500
if sp500_check:
    with inpcol1.expander("S&P 500"):
        sp500_chartcol1, sp500_chartcol2 = st.columns(2)
        #EQUITY MARKET -> S&P500 -> RSI and MA selection & CHART
        
        sp500_rsi_length=sp500_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="S&P500 rsi length selection")
        sp500_ma_length=sp500_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="S&P500 ma length selection")
        
        sp500 = Generate_Equity()
        sp500.get_database(["^GSPC"], start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=sp500_rsi_length, ma_length=sp500_ma_length)
        
        sp500_chartcol1.line_chart(sp500.lf.select(["rsi"]).collect(), height=200, use_container_width=True)
        sp500_chartcol2.line_chart(sp500.lf.select(["Date", "Close", "ma"]).collect(), x="Date", y=["Close", "ma"], height=200, use_container_width=True)

        # EQUITY MARKET -> S&P 500 -> % CHANGE / Price vs MA / RSI
        sp500_col1,sp500_col2=st.columns(2)
        sp500_rsi_on = sp500_col1.toggle("RSI", key="sp500 RSI toggle")
        sp500_ma_on = sp500_col2.toggle("Moving Average", key="sp500 MA toggle")

        # EQUITY MARKET -> S&P 500 -> RSI
        if sp500_rsi_on:
            sp500_rsi_comparator = sp500_col1.selectbox("S&P comparator",('Greater than', 'Less than'))
            sp500_rsi_selection = sp500_col1.number_input("Select value", min_value=0.0, step=1.0, key="S&P rsi selection")
            
            sp500.metric_vs_selection_cross("rsi_vs_selection",sp500_rsi_comparator, [sp500_rsi_selection])
            filtered_db_list.append(sp500.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" S&P500 Price {sp500_rsi_comparator} {sp500_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", S&P500 Price {sp500_rsi_comparator} {sp500_rsi_selection}"
            equity_counter+=1

        # EQUITY MARKET -> S&P 500 -> Moving Average
        if sp500_ma_on:
            sp500_ma_comparator = sp500_col2.selectbox(f"sp500 Price > or < {sp500_ma_length} day Moving Average", ('Greater than', 'Less than'))
            
            sp500.metric_vs_selection_cross('price_vs_ma', sp500_ma_comparator)
            filtered_db_list.append(sp500.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" S&P500 Price {sp500_ma_comparator} S&P500 {sp500_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", S&P500 Price {sp500_ma_comparator} S&P500 {sp500_ma_length} day Moving Average"
            equity_counter+=1
        
        # EQUITY MARKET -> S&P 500 -> % CHANGE / Price vs MA / RSI
        sp500_pct_on = sp500_col1.toggle("% Change", key="sp500 % Change toggle")

        # EQUITY MARKET -> S&P 500 -> % CHANGE
        if sp500_pct_on:
            sp500_col2.line_chart(sp500.lf.select(["Date", "% Change"]).collect(), x="Date", y="% Change", height=200, use_container_width=True)

            sp500_pct_lower = sp500_col1.number_input("Between lower value", step=0.5, key="sp500 between lower value")
            sp500_pct_higher = sp500_col1.number_input("Between higher value", step=0.6, key="sp500 between higher value")
            
            sp500.metric_vs_selection_cross("%_change", "Between", [sp500_pct_lower, sp500_pct_higher])
            
            if equity_counter==0:
                equity_filters_applied_sentence+=f" S&P500 % change between {sp500_pct_lower}% and {sp500_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", S&P500 % change between {sp500_pct_lower}% and {sp500_pct_higher}%"
            equity_counter+=1
            
# EQUITY MARKET -> Nasdaq
if nasdaq_check:
    with inpcol1.expander("Nasdaq"):
        ndx_chartcol1, ndx_chartcol2 = st.columns(2)
        #EQUITY MARKET -> NASDAQ -> RSI and MA selection & CHART
        ndx_rsi_length=ndx_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="Nasdaq rsi length selection")
        ndx_ma_length=ndx_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="Nasdaq ma length selection")
        
        ndx = Generate_Equity()
        ndx.get_database("^IXIC", start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=ndx_rsi_length, ma_length=ndx_ma_length)
        
        ndx_chartcol1.line_chart(ndx.lf.select(["Date", "rsi"]).collect(), x="Date", y="rsi", height=200, use_container_width=True)
        ndx_chartcol2.line_chart(ndx.lf.select(["Date", "Close", "ma"]).collect(), x="Date", y=["Close", "ma"], height=200, use_container_width=True)

        # EQUITY MARKET -> Nasdaq -> % CHANGE / Price vs MA / RSI
        ndx_col1,ndx_col2=st.columns(2)
        ndx_rsi_on = ndx_col1.toggle("RSI", key="ndx RSI toggle")
        ndx_ma_on = ndx_col2.toggle("Moving Average", key="ndx MA toggle")

        # EQUITY MARKET -> Nasdaq -> RSI
        if ndx_rsi_on:
            ndx_rsi_comparator = ndx_col1.selectbox("Nasdaq comparator",('Greater than', 'Less than'))
            ndx_rsi_selection = ndx_col1.number_input("Select value", min_value=0.0, step=1.0, key="Nasdaq rsi selection")
            
            ndx.metric_vs_selection_cross("rsi_vs_selection", ndx_rsi_comparator, [ndx_rsi_selection])
            filtered_db_list.append(ndx.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq Price {ndx_rsi_comparator} {ndx_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", Nasdaq Price {ndx_rsi_comparator} {ndx_rsi_selection}"
            equity_counter+=1
        # EQUITY MARKET -> Nasdaq -> Moving Average
        if ndx_ma_on:
            ndx_ma_comparator = ndx_col2.selectbox(f"ndx Price > or < {ndx_ma_length} day Moving Average", ('Greater than', 'Less than'))

            ndx.metric_vs_selection_cross("price_vs_ma", ndx_ma_comparator)
            filtered_db_list.append(ndx.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq Price {ndx_ma_comparator} Nasdaq {ndx_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", Nasdaq Price {ndx_ma_comparator} Nasdaq {ndx_ma_length} day Moving Average"
            equity_counter+=1
        # EQUITY MARKET -> Nasdaq -> % CHANGE / Price vs MA / RSI
        ndx_pct_on = ndx_col1.toggle("% Change", key="ndx % Change toggle")

        # EQUITY MARKET -> Nasdaq -> % CHANGE
        if ndx_pct_on:
            ndx_pct_lower = ndx_col1.number_input("Between lower value", step=0.5, key="ndx between lower value")
            ndx_pct_higher = ndx_col1.number_input("Between higher value", step=0.6, key="ndx between higher value")

            ndx.metric_vs_selection_cross("%_change", "Between", [ndx_pct_lower, ndx_pct_higher])
            filtered_db_list.append(ndx.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Nasdaq % change between {ndx_pct_lower}% and {ndx_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", Nasdaq % change between {ndx_pct_lower}% and {ndx_pct_higher}%"
            equity_counter+=1

            ndx_col2.line_chart(ndx.lf.select(["Date", "% Change"]).collect(), x="Date", y="% Change", height=200, use_container_width=True)

# EQUITY MARKET -> Russell 2000
if russell2000_check:
    with inpcol1.expander("Russell 2000"):
        rus2k_chartcol1, rus2k_chartcol2 = st.columns(2)
        #EQUITY MARKET -> Russell 2000 -> RSI and MA selection & CHART
        rus2k_rsi_length=rus2k_chartcol1.number_input("Select  RSI days", min_value=0, step=1, value=22, key="Russell 2000 rsi length selection")
        rus2k_ma_length=rus2k_chartcol2.number_input("Select MA days", min_value=0, step=1, value=50, key="Russell 2000 ma length selection")
        
        rus2k = Generate_Equity()
        rus2k.get_database("^RUT", start_date=input_start_date, end_date=input_end_date, interval=input_interval, rsi_value=rus2k_rsi_length, ma_length=rus2k_ma_length)
        
        rus2k_chartcol1.line_chart(rus2k.lf.select(["Date", "rsi"]).collect(), x="Date", y="rsi", height=200, use_container_width=True)
        rus2k_chartcol2.line_chart(rus2k.lf.select(["Date", "Close", "ma"]).collect(), x="Date", y=["Close", "ma"], height=200, use_container_width=True)

        # EQUITY MARKET -> Russell 2000 -> % CHANGE / Price vs MA / RSI
        rus2k_col1,rus2k_col2=st.columns(2)
        rus2k_rsi_on=rus2k_col1.toggle("RSI", key="rus2k RSI toggle")
        rus2k_ma_on=rus2k_col2.toggle("Moving Average", key="rus2k MA toggle")

        # EQUITY MARKET -> Russell 2000 -> RSI
        if rus2k_rsi_on:
            rus2k_rsi_comparator = rus2k_col1.selectbox("Russell 2000 comparator",('Greater than', 'Less than'))
            rus2k_rsi_selection = rus2k_col1.number_input("Select value", min_value=0.0, step=1.0, key="Russell 2000 rsi selection")

            rus2k.metric_vs_selection_cross("rsi_vs_selection", rus2k_rsi_comparator, [rus2k_rsi_selection])
            filtered_db_list.append(rus2k.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 Price {rus2k_rsi_comparator} {rus2k_rsi_selection}"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 Price {rus2k_rsi_comparator} {rus2k_rsi_selection}"
            equity_counter+=1
        # EQUITY MARKET -> Nasdaq -> Moving Average
        if rus2k_ma_on:
            rus2k_ma_comparator = rus2k_col2.selectbox(f"rus2k Price > or < {rus2k_ma_length} day Moving Average", ('Greater than', 'Less than'))

            rus2k.metric_vs_selection_cross("price_vs_ma", rus2k_ma_comparator)
            filtered_db_list.append(rus2k.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 Price {rus2k_ma_comparator} Russell 2000 {rus2k_ma_length} day Moving Average"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 Price {rus2k_ma_comparator} Russell 2000 {rus2k_ma_length} day Moving Average"
            equity_counter+=1
        # EQUITY MARKET -> Russell 2000 -> % CHANGE / Price vs MA / RSI
        rus2k_pct_on = rus2k_col1.toggle("% Change", key="rus2k % Change toggle")

        # EQUITY MARKET -> Russell 2000 -> % CHANGE
        if rus2k_pct_on:
            rus2k_pct_lower = rus2k_col1.number_input("Between lower value", step=0.5, key="rus2k between lower value")
            rus2k_pct_higher = rus2k_col1.number_input("Between higher value", step=0.6, key="rus2k between higher value")

            rus2k.metric_vs_selection_cross("%_change", "Between", [rus2k_pct_lower, rus2k_pct_higher])
            filtered_db_list.append(rus2k.filtered_dates)

            if equity_counter==0:
                equity_filters_applied_sentence+=f" Russell 2000 % change between {rus2k_pct_lower}% and {rus2k_pct_higher}%"
            else:
                equity_filters_applied_sentence+=f", Russell 2000 % change between {rus2k_pct_lower}% and {rus2k_pct_higher}%"
            equity_counter+=1

            rus2k_col2.line_chart(rus2k.lf.select(["Date", "% Change"]).collect(),x="Date", y="% Change", height=200, use_container_width=True)

# EQUITY MARKET -> EQUTIY RATIO
if equityratio_check:
    with inpcol1.expander("Equity Ratio"):
        eq_ratio_col1, eq_ratio_col2 = st.columns(2)
        eq_ratio_numerator_selection = eq_ratio_col1.selectbox("Numerator", ("None", "Nasdaq", "S&P 500", "S&P 500 Equal Weight", "Russell 2000"), key="equity ratio numerator selector")
        eq_ratio_denominator_selection = eq_ratio_col2.selectbox("Denominator", ("None", "Nasdaq", "S&P 500", "S&P 500 Equal Weight", "Russell 2000"), key="equity ratio denominator selector")
        
        if not eq_ratio_numerator_selection == "None" and not eq_ratio_denominator_selection == "None":
            eq_ratio_rsi_length = eq_ratio_col1.number_input("Select RSI days", min_value=0, step=1, value=22, key="equity ratio RSI length")
            eq_ratio_ma_length = eq_ratio_col2.number_input("Select MA days", min_value=0, step=1, value=50, key="equity ratio MA length")
            
            equity_ratio = Generate_Equity()
            equity_ratio.generate_ratio(eq_ratio_numerator_selection, eq_ratio_denominator_selection, input_start_date, input_end_date, input_interval, eq_ratio_rsi_length, eq_ratio_ma_length)
            
            equity_df = equity_ratio.lf.collect()
            eq_ratio_col1.line_chart(equity_df.select(["Date", "rsi"]), x="Date", y="rsi", height=200, use_container_width=True)
            eq_ratio_col2.dataframe(equity_df.select(["Date", "Close", "ma", "% Change"]), height=200, use_container_width=True, hide_index=True, column_config={
            "Date": st.column_config.DateColumn(
                "Date", format="YYYY-MM-DD"
            ),
            '% Change': st.column_config.NumberColumn(
                "% Change",
                format="%.2f%%"
            )
        })

            # EQUITY MARKET -> EQUITY RATIO -> RSI / MA / % CHANGE
            eq_ratio_rsi_on = eq_ratio_col1.toggle("RSI", key="equity ratio RSI")
            eq_ratio_ma_on = eq_ratio_col2.toggle("MA", key="equity ratio MA")

            # EQUITY MARKET -> EQUITY RATIO -> RSI
            if eq_ratio_rsi_on:
                eq_ratio_comparator = eq_ratio_col1.selectbox("Ratio comparator", ("Greater than", "Less than"), key="equity ratio comparator")
                eq_ratio_rsi_selection = eq_ratio_col2.number_input("Select RSI value", min_value=0.0, step=1.0, key="equity ratio RSI selection")

                equity_ratio.metric_vs_selection_cross("rsi_vs_selection", eq_ratio_comparator, [eq_ratio_rsi_selection])
                filtered_db_list.append(equity_ratio.filtered_dates)

                if equity_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio Price {eq_ratio_comparator} {eq_ratio_rsi_selection}"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio Price {eq_ratio_comparator} {eq_ratio_rsi_selection}"
                equity_counter+=1
            
            # EQUITY MARKET -> EQUITY RATIO -> MA
            if eq_ratio_ma_on:
                eq_ratio_ma_comparator = eq_ratio_col2.selectbox(f"Equity Ratio > or < {eq_ratio_ma_length} day Moving Average", ('Greater than','Less than'))

                equity_ratio.metric_vs_selection_cross("price_vs_ma", eq_ratio_ma_comparator)
                filtered_db_list.append(equity_ratio.filtered_dates)                
                
                if equity_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio Price {eq_ratio_ma_comparator} Equity Ratio {eq_ratio_ma_length} day Moving Average"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio Price {eq_ratio_ma_comparator} Equity Ratio {eq_ratio_ma_length} day Moving Average"
                equity_counter+=1
            
            # EQUITY MARKET -> EQUITY RATIO -> % CHANGE
            eq_ratio_pct_on=eq_ratio_col1.toggle("% Change", key="equity ratio % change")
            eq_ratio_level_on = eq_ratio_col2.toggle("Ratio level", key="equity_ratio_level")

            # EQUITY MARKET -> EQUITY RATIO -> % CHANGE
            if eq_ratio_pct_on:
                eqratio_pct_lower = eq_ratio_col1.number_input("Between lower value", step=0.5, key="equity ratio between lower value")
                eqratio_pct_higher = eq_ratio_col1.number_input("Between higher value", step=0.6, key="equity ratio between higher value")

                equity_ratio.metric_vs_selection_cross("%_change", "Between", [eqratio_pct_lower, eqratio_pct_higher])
                filtered_db_list.append(equity_ratio.filtered_dates)

                if equity_counter==0:
                    equity_filters_applied_sentence+=f" Equity Ratio % change between {eqratio_pct_lower}% and {eqratio_pct_higher}%"
                else:
                    equity_filters_applied_sentence+=f", Equity Ratio % change between {eqratio_pct_lower}% and {eqratio_pct_higher}%"
                equity_counter+=1
            
            if eq_ratio_level_on:
                eq_ratio_level_comparator = eq_ratio_col2.selectbox("Ratio comparator", ("Greater than", "Less than"))
                eq_ratio_level_selection = eq_ratio_col2.number_input("Select value", min_value=0.0, step=0.1, key="ratio_level_selection")

                equity_ratio.metric_vs_selection_cross("current_price", eq_ratio_level_comparator, [eq_ratio_level_selection])
                filtered_db_list.append(equity_ratio.filtered_dates)

                if equity_counter==0:
                    equity_filters_applied_sentence+=f" Ratio {eq_ratio_level_comparator} {eq_ratio_level_selection}"
                else:
                    equity_filters_applied_sentence+=f"Ratio {eq_ratio_level_comparator} {eq_ratio_level_selection}"
                equity_counter+=1

# EQUITY MARKET -> SUMMARY
inpcol1.write("*"+equity_filters_applied_sentence+"*")

# DEBT MARKET
debt_filters_applied_sentence = "Debt filters to apply:"
debt_market = inpcol2.popover("Debt Market")
yieldspread_check = debt_market.checkbox("Market Yield Spread (Yield Curve)", False)
usfedfundrate_check = debt_market.checkbox("US Federal Funds Rate", False)
us_treasury_sec_check = debt_market.checkbox("US Treasury Securities", False)
debt_counter=0

# DEBT MARKET -> YIELD SPREAD
if yieldspread_check:
    with inpcol2.expander("Yield Spread"):
        yieldspread = Generate_Debt()
        spreadcol1, spreadcol2 = st.columns(2)

        # DEBT MARKET -> YIELD SPREAD -> Long Term
        lt_maturity_selection = spreadcol1.selectbox("Long-Term Maturity", ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"), index=8)

        # DEBT MARKET -> YIELD SPREAD -> Short Term
        st_maturity_selection = spreadcol2.selectbox("Short-Term Maturity", ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"), index=4)

        # DEBT MARKET -> YIELD SPREAD
        yieldspread.generate_yield_spread(input_start_date, input_end_date, lt_maturity_selection, st_maturity_selection, selection_interval)

        spreadcol1.line_chart(yieldspread.lf.select(["Date", f'{lt_maturity_selection} Rate', f'{st_maturity_selection} Rate', 'Rate Spread']).collect(), height=200, use_container_width=True,x="Date", y=[f'{lt_maturity_selection} Rate', f'{st_maturity_selection} Rate', 'Rate Spread'], color=['#c9c9e6', '#cce6c9', '#be2a25'])

        spreadcol2.dataframe(yieldspread.lf.select(["Date", 'Rate Spread', "Spread % Change"]).collect(), height=207, hide_index=True,column_order=["Date",'Rate Spread', 'Spread % Change'],column_config={
            "Date": st.column_config.DateColumn(
                "Date", format="YYYY-MM-DD"
            ),
            'Spread % Change': st.column_config.NumberColumn(
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

            yieldspread.metric_vs_selection_cross("yield_spread", spread_level_comparator, [spread_level_selection])
            filtered_db_list.append(yieldspread.filtered_dates)

            if debt_counter == 0:            
                debt_filters_applied_sentence+=f" Spread Level {spread_level_comparator} {spread_level_selection}"
            else:
                debt_filters_applied_sentence+=f", Spread Level {spread_level_comparator} {spread_level_selection}"
            debt_counter+=1
        
        if spread_pct_on:
            spread_pct_lower = spreadcol2.number_input("Between lower value", step=0.5, key="spread between lower value")
            spread_pct_higher = spreadcol2.number_input("Between higher value", step=0.5, key="spread between higher value")

            yieldspread.metric_vs_selection_cross("spread_%_change", "Between", [spread_pct_lower, spread_pct_higher])
            filtered_db_list.append(yieldspread.filtered_dates)

            if debt_counter==0:
                debt_filters_applied_sentence+=f" Spread % change between {spread_pct_lower}% and {spread_pct_higher}%"
            else:
                debt_filters_applied_sentence+=f", Spread % change between {spread_pct_lower}% and {spread_pct_higher}%"
            debt_counter+=1

if usfedfundrate_check:    
    with inpcol2.expander("US Federal Funds Rate"):
        usfedfund = Generate_Debt()
        usfedfund.get_database("US FED FUNDS", input_start_date, input_end_date, selection_interval)
        
        usfedr_col1, usdfedr_col2 = st.columns(2)

        # DEBT MARKET -> US FED FUND RATE -> Change
        usfedr_col1.line_chart(usfedfund.lf.collect(),x="Date", y=['US FED FUNDS Rate'], height=200)
        
        usfedrate_level_on = usdfedr_col2.toggle("US Fed Funds Rate Change", key="US Fed Funds Rate Change")

        if usfedrate_level_on:
            usfedrate_level_selection_lower = usdfedr_col2.number_input("Increase/Decrease Between (lower value)", step=0.25, value=-0.30)
            usfedrate_level_selection_higher = usdfedr_col2.number_input("Increase/Decrease Between (higher value)", step=0.25, value=-0.20)

            usfedfund.metric_vs_selection_cross("%_change", "Between", [usfedrate_level_selection_lower, usfedrate_level_selection_higher])
            filtered_db_list.append(usfedfund.filtered_dates)

            if debt_counter==0:
                debt_filters_applied_sentence+=f" US Fed Funds Rate change between {usfedrate_level_selection_lower}% and {usfedrate_level_selection_higher}%"
            else:
                debt_filters_applied_sentence+=f", US Fed Funds Rate change between {usfedrate_level_selection_lower}% and {usfedrate_level_selection_higher}%"
            debt_counter+=1

if us_treasury_sec_check:
    with inpcol2.expander("US Treasury Securities"):
        us_treasury_db=Generate_Debt()

        us_treasury_selection = st.selectbox("Treasury Maturity", ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"))

        us_treasury_db.get_database(us_treasury_selection, input_start_date, input_end_date, selection_interval)
        
        us_treasury1, us_treasury2 = st.columns(2)

        us_treasury1.line_chart(us_treasury_db.lf.select(["Date", f"{us_treasury_selection} Rate"]).collect(), height=200, use_container_width=True, x="Date", y=[f"{us_treasury_selection} Rate"])

        us_treasury2.dataframe(us_treasury_db.lf.select(["Date", f"{us_treasury_selection} Rate", "% Change"]).collect(), height=200, hide_index=True, column_order=["Date", f"{us_treasury_selection} Rate", "% Change"], column_config={
            "Date": st.column_config.DateColumn(
                "Date", format="YYYY-MM-DD"
            ),
            "% Change": st.column_config.NumberColumn(
                "% Change", format="%.2f%%"
            )
        })
        
        treasury_level_on=us_treasury1.toggle("Treasury Level", key="US_Treasury_level_toggle")
        treasury_pct_on=us_treasury2.toggle("Treasury % Change", key="US_Treasury_pctchange_toggle")

        if treasury_level_on:
            us_treasury_level_comparator = us_treasury1.selectbox("Level Comparator", ("Greater than", "Less than"))
            us_treasury_level_selection = us_treasury1.number_input("Select value", step=1.0, value=1.0)
            us_treasury_db.metric_vs_selection_cross("current_price", us_treasury_level_comparator, [us_treasury_level_selection])
            filtered_db_list.append(us_treasury_db.filtered_dates)

            if debt_counter == 0:            
                debt_filters_applied_sentence+=f"{us_treasury_selection} {us_treasury_level_comparator} {us_treasury_level_selection}"
            else:
                debt_filters_applied_sentence+=f", {us_treasury_selection} {us_treasury_level_comparator} {us_treasury_level_selection}"
            debt_counter+=1

        if treasury_pct_on:
            us_treasury_pct_lower = us_treasury2.number_input("Between lower value", step=0.5, key="treasury_between_lower_value")
            us_treasury_pct_higher = us_treasury2.number_input("Between higher value", step=0.5, key="treasury_between_higher_value")

            us_treasury_db.metric_vs_selection_cross("%_change", "Between", [us_treasury_pct_lower, us_treasury_pct_higher])
            filtered_db_list.append(us_treasury_db.filtered_dates)

            if debt_counter == 0:            
                debt_filters_applied_sentence+=f"{us_treasury_selection} % change between{us_treasury_pct_lower} and {us_treasury_pct_higher}"
            else:
                debt_filters_applied_sentence+=f", {us_treasury_selection} % change between{us_treasury_pct_lower} and {us_treasury_pct_higher}"
            debt_counter+=1

# DEBT MARKET -> SUMMARY    
inpcol2.write("*"+debt_filters_applied_sentence+"*")

# ECONONOMIC & STATISTICAL
econ_stat_filters_applied_sentence = "Economical & Statistical filters applied:"
econ_stat = inpcol3.popover("Economic & Statistical Figures")
sahm_check = econ_stat.checkbox("Sahm Rule", False)
economic_uncertainty_check = econ_stat.checkbox("US Economic Policy Uncertainty")
sp500_volatility_check = econ_stat.checkbox("S&P 500 Volatility Index (VIX)", False)
ndx100_volatility_check = econ_stat.checkbox("Nasdaq 100 Volatility Index (VIX)", False)
rus2k_volatility_check = econ_stat.checkbox("Russell 2000 Volatility Index (VIX)", False)
crudeoil_volatility_check = econ_stat.checkbox("Crude Oil Volatility Index (VIX)", False)

econ_stat_counter=0

# ECONONOMIC & STATISTICAL -> SAHM VALUES
if sahm_check:
    with inpcol3.expander("Sahm Rule"):
        sahm_rule_db = Generate_Indicator()
        sahm_rsi_length = st.number_input("Select RSI days", min_value=1,step=1, value=22, key="sahm_rsi_length")

        sahm_rule_db.get_database("Sahm Rule", input_start_date, input_end_date, sahm_rsi_length)
        
        statcol1, statcol2 = st.columns(2)
        statcol1.line_chart(sahm_rule_db.lf.select(["Date", "Sahm Rule"]).collect(), x="Date", y=["Sahm Rule"], height=200, use_container_width=True)
        statcol2.line_chart(sahm_rule_db.lf.select(["Date", "rsi"]).collect(), x="Date", y=["rsi"], height=200, use_container_width=True)

        sahm_value_on = statcol1.toggle("Sahm Rule Value", key="sahmrule_value_toggle")
        sahm_rsi_on = statcol2.toggle("Sahm Rule RSI", key="sahmrule_rsi_toggle")

        if sahm_value_on:
            sahm_value_comparator = statcol1.selectbox("Sahm Rule Comparator", ("Greater than", "Less than"))
            sahm_value_selection = statcol1.number_input("Select Value", min_value=0.0, step=1.0, key="sahm_value_selection")
            sahm_rule_db.metric_vs_selection_cross('sahm_rule_value', sahm_value_comparator, [sahm_value_selection])
            filtered_db_list.append(sahm_rule_db.filtered_dates)
            
            if econ_stat_filters_applied_sentence==0:
                econ_stat_filters_applied_sentence+=f"Sahm is {sahm_value_comparator} {sahm_value_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", Sahm is {sahm_value_comparator} {sahm_value_selection}"
            econ_stat_counter+=1
        
        if sahm_rsi_on:
            sahm_rsi_comparator = statcol2.selectbox("Sahm Rule RSI Comparator", ("Greater than", "Less than"))
            sahm_rsi_selection = statcol2.number_input("Select value", min_value=0.0, step=1.0, key="sahm_rule_rsi_selection")

            sahm_rule_db.metric_vs_selection_cross('rsi_vs_selection', sahm_rsi_comparator, [sahm_rsi_selection])
            filtered_db_list.append(sahm_rule_db.filtered_dates)

            if econ_stat_filters_applied_sentence==0:
                econ_stat_filters_applied_sentence+=f"Sahm RSI {sahm_rsi_comparator} {sahm_rsi_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", Sahm RSI {sahm_rsi_comparator} {sahm_rsi_selection}"
            econ_stat_counter+=1

# ECONONOMIC & STATISTICAL -> Economic Policy Uncertainty
if economic_uncertainty_check:
    with inpcol3.expander("US Economic Policy Uncertainty Index (US EPU)"):
        us_epu_db = Generate_Indicator()
        us_epu_rsilength = st.number_input("Select RSI days", min_value=1,step=1, value=22, key="us_epu_rsi_length")

        us_epu_db.get_database("US Economic Policy Uncertainty Index", input_start_date, input_end_date, us_epu_rsilength)

        statcol1, statcol2 = st.columns(2)

        statcol1.line_chart(us_epu_db.lf.select(["Date", "US Economic Policy Uncertainty Index"]).collect(), x="Date", y="US Economic Policy Uncertainty Index", height=200, use_container_width=True)
        statcol2.line_chart(us_epu_db.lf.select(["Date", "rsi"]).collect(), x="Date", y="rsi", height=200, use_container_width=True) #TODO convert to different type of line chart to fix y-axis

        usepu_value_on = statcol1.toggle("USEPU Index Value", key="usepu_value_toggle")
        usepu_rsi_on = statcol2.toggle("USEPU Index RSI", key="usepu_rsi_toggle")

        if usepu_value_on:
            usepu_value_comparator = statcol1.selectbox("USEPU Comparator", ("Greater than", "Less than"))
            usepu_value_selection = statcol1.number_input("Select Value", min_value=0.0, step=1.0, key="usepu_value_selection")
            us_epu_db.metric_vs_selection_cross("usepu_value", usepu_value_comparator, [usepu_value_selection])
            filtered_db_list.append(us_epu_db.filtered_dates)

            if econ_stat_filters_applied_sentence==0:
                econ_stat_filters_applied_sentence+=f"US EPU is {usepu_value_comparator} {usepu_value_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", US EPU is {usepu_value_comparator} {usepu_value_selection}"
            econ_stat_counter+=1

        if usepu_rsi_on:
            usepu_rsi_comparator = statcol2.selectbox("US EPU RSI Comparator", ("Greater than", "Less than"))
            usepu_rsi_selection = statcol2.number_input("Select value", min_value=0.0, step=1.0, key="usepu_rsi_selection")
            us_epu_db.metric_vs_selection_cross("usepu_value", usepu_rsi_comparator, [usepu_rsi_selection])
            filtered_db_list.append(us_epu_db.filtered_dates)

            if econ_stat_filters_applied_sentence==0:
                econ_stat_filters_applied_sentence+=f"US EPU RSI {usepu_rsi_comparator} {usepu_rsi_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", US EPU RSI {usepu_rsi_comparator} {usepu_rsi_selection}"
            econ_stat_counter+=1

# ECONONOMIC & STATISTICAL -> S&P 500 VOLATILITY INDEX
if sp500_volatility_check:
    with inpcol3.expander("S&P 500 Volatility Index"):
        sp500vix=Generate_Equity()
        sp500vix.get_database(["^VIX"], input_start_date, input_end_date, input_interval)
        st.line_chart(sp500vix.lf.select(["Date", "Close"]).collect(), x="Date", y="Close", height=200, use_container_width=True)

        sp500vixcol1, sp500vixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        sp500vix_level_on = sp500vixcol1.toggle("Price Level", key="sp500vix_p_toggle")
        sp500vix_pct_on = sp500vixcol2.toggle("% Change", key="sp500vix_%_toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> sp500VIX LEVEL
        if sp500vix_level_on:
            sp500vix_level_comparator = sp500vixcol1.selectbox("sp500 VIX Comparator",('Greater than', 'Less than'))
            sp500vix_level_selection = sp500vixcol1.number_input("Select value", min_value=0.0, step=0.5)
            
            sp500vix.metric_vs_selection_cross(comparison_type='current_price',selected_value=[sp500vix_level_selection],comparator=sp500vix_level_comparator)
            filtered_db_list.append(sp500vix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"S&P 500 VIX level {sp500vix_level_comparator} {sp500vix_level_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", S&P 500 VIX level {sp500vix_level_comparator} {sp500vix_level_selection}"
            econ_stat_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> VIX % CHANGE
        if sp500vix_pct_on:
            sp500vix_pct_lower = sp500vixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            sp500vix_pct_higher = sp500vixcol2.number_input("Between higher value", step=0.6, key="sp500vix between higher value")

            sp500vix.metric_vs_selection_cross(comparison_type="%_change",selected_value=[sp500vix_pct_lower, sp500vix_pct_higher], comparator="Between")
            filtered_db_list.append(sp500vix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"S&P 500 VIX % change between {sp500vix_pct_lower}% and {sp500vix_pct_higher}%"
            else:
                econ_stat_filters_applied_sentence+=f", S&P 500 VIX % change between {sp500vix_pct_lower}% and {sp500vix_pct_higher}%"
            econ_stat_counter+=1

# ECONONOMIC & STATISTICAL -> Russell 2000 VOLATILITY INDEX
if rus2k_volatility_check:
    with inpcol3.expander("Russell 2000 Volatility Index"):
        rus2kvix=Generate_Equity()
        rus2kvix.get_database(["^RVX"], input_start_date, input_end_date, input_interval)
        st.line_chart(rus2kvix.lf.select(["Date", "Close"]).collect(), x="Date", y="Close", height=200, use_container_width=True)

        rus2kvixcol1, rus2kvixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        rus2kvix_level_on = rus2kvixcol1.toggle("Price Level", key="rus2kvix_p_toggle")
        rus2kvix_pct_on = rus2kvixcol2.toggle("% Change", key="rus2kvix_%_toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> sp500VIX LEVEL
        if rus2kvix_level_on:
            rus2kvix_level_comparator = rus2kvixcol1.selectbox("Russell 2000 VIX Comparator",('Greater than', 'Less than'))
            rus2kvix_level_selection = rus2kvixcol1.number_input("Select value", min_value=0.0, step=0.5)
            
            rus2kvix.metric_vs_selection_cross(comparison_type='current_price',selected_value=[rus2kvix_level_selection],comparator=rus2kvix_level_comparator)
            filtered_db_list.append(rus2kvix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Russell 2000 VIX level {rus2kvix_level_comparator} {rus2kvix_level_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", Russell 2000 VIX level {rus2kvix_level_comparator} {rus2kvix_level_selection}"
            econ_stat_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> Russell 2000 VIX % CHANGE
        if rus2kvix_pct_on:
            rus2kvix_pct_lower = rus2kvixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            rus2kvix_pct_higher = rus2kvixcol2.number_input("Between higher value", step=0.6, key="rus2kvix between higher value")

            rus2kvix.metric_vs_selection_cross(comparison_type="%_change",selected_value=[rus2kvix_pct_lower, rus2kvix_pct_higher], comparator="Between")
            filtered_db_list.append(rus2kvix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Russell 2000 VIX % change between {rus2kvix_pct_lower}% and {rus2kvix_pct_higher}%"
            else:
                econ_stat_filters_applied_sentence+=f", Russell 2000 VIX % change between {rus2kvix_pct_lower}% and {rus2kvix_pct_higher}%"
            econ_stat_counter+=1

# ECONONOMIC & STATISTICAL -> Nasdaq 100 VOLATILITY INDEX
if ndx100_volatility_check:
    with inpcol3.expander("Nasdaq 100 Volatility Index"):
        ndx100vix=Generate_Equity()
        ndx100vix.get_database(["^VXN"], input_start_date, input_end_date, input_interval)
        st.line_chart(ndx100vix.lf.select(["Date", "Close"]).collect(), x="Date", y="Close", height=200, use_container_width=True)

        ndx100vixcol1, ndx100vixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        ndx100vix_level_on = ndx100vixcol1.toggle("Price Level", key="ndx100vix_p_toggle")
        ndx100vix_pct_on = ndx100vixcol2.toggle("% Change", key="ndx100vix_%_toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> sp500VIX LEVEL
        if ndx100vix_level_on:
            ndx100vix_level_comparator = ndx100vixcol1.selectbox("Nasdaq 100 VIX Comparator",('Greater than', 'Less than'))
            ndx100vix_level_selection = ndx100vixcol1.number_input("Select value", min_value=0.0, step=0.5)
            
            ndx100vix.metric_vs_selection_cross(comparison_type='current_price',selected_value=[ndx100vix_level_selection],comparator=ndx100vix_level_comparator)
            filtered_db_list.append(ndx100vix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Nasdaq 100 VIX level {ndx100vix_level_comparator} {ndx100vix_level_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", Nasdaq 100 VIX level {ndx100vix_level_comparator} {ndx100vix_level_selection}"
            econ_stat_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> Nasdaq 100 VIX % CHANGE
        if ndx100vix_pct_on:
            ndx100vix_pct_lower = ndx100vixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            ndx100vix_pct_higher = ndx100vixcol2.number_input("Between higher value", step=0.6, key="ndx100vix between higher value")

            ndx100vix.metric_vs_selection_cross(comparison_type="%_change",selected_value=[ndx100vix_pct_lower, ndx100vix_pct_higher], comparator="Between")
            filtered_db_list.append(ndx100vix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Nasdaq 100 VIX % change between {ndx100vix_pct_lower}% and {ndx100vix_pct_higher}%"
            else:
                econ_stat_filters_applied_sentence+=f", Nasdaq 100 VIX % change between {ndx100vix_pct_lower}% and {ndx100vix_pct_higher}%"
            econ_stat_counter+=1

# ECONONOMIC & STATISTICAL -> Crude Oil VOLATILITY INDEX
if crudeoil_volatility_check:
    with inpcol3.expander("Crude Oil Volatility Index"):
        crudeoilvix=Generate_Equity()
        crudeoilvix.get_database(["^OVX"], input_start_date, input_end_date, input_interval)
        st.line_chart(crudeoilvix.lf.select(["Date", "Close"]).collect(), x="Date", y="Close", height=200, use_container_width=True)

        crudeoilvixcol1, crudeoilvixcol2 = st.columns(2)
    # EQUITY MARKET -> VOLATIALITY INDEX -> VIX LEVEL / VIX %
        crudeoilvix_level_on = crudeoilvixcol1.toggle("Price Level", key="crudeoilvix_p_toggle")
        crudeoilvix_pct_on = crudeoilvixcol2.toggle("% Change", key="crudeoilvix_%_toggle")
    # EQUITY MARKET -> VOLATILITY INDEX -> VIX LEVEL
        if crudeoilvix_level_on:
            crudeoilvix_level_comparator = crudeoilvixcol1.selectbox("crudeoilVIX Comparator",('Greater than', 'Less than'))
            crudeoilvix_level_selection = crudeoilvixcol1.number_input("Select value", min_value=0.0, step=0.5)
            
            crudeoilvix.metric_vs_selection_cross(comparison_type='current_price',selected_value=[crudeoilvix_level_selection],comparator=crudeoilvix_level_comparator)
            filtered_db_list.append(crudeoilvix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Crude Oil VIX level {crudeoilvix_level_comparator} {crudeoilvix_level_selection}"
            else:
                econ_stat_filters_applied_sentence+=f", Crude Oil VIX level {crudeoilvix_level_comparator} {crudeoilvix_level_selection}"
            econ_stat_counter+=1
    #  EQUITY MARKET -> VOLATILITY INDEX -> Crude Oil VIX % CHANGE
        if crudeoilvix_pct_on:
            crudeoilvix_pct_lower = crudeoilvixcol2.number_input("Between lower value", step=0.5, key="vix between lower value")
            crudeoilvix_pct_higher = crudeoilvixcol2.number_input("Between higher value", step=0.6, key="crudeoilvix between higher value")

            crudeoilvix.metric_vs_selection_cross(comparison_type="%_change",selected_value=[crudeoilvix_pct_lower, crudeoilvix_pct_higher], comparator="Between")
            filtered_db_list.append(crudeoilvix.filtered_dates)
            
            if econ_stat_counter==0:
                econ_stat_filters_applied_sentence+=f"Crude Oil VIX % change between {crudeoilvix_pct_lower}% and {crudeoilvix_pct_higher}%"
            else:
                econ_stat_filters_applied_sentence+=f", Crude Oil VIX % change between {crudeoilvix_pct_lower}% and {crudeoilvix_pct_higher}%"
            econ_stat_counter+=1

# Economic/Stat -> SUMMARY    
inpcol3.write("*"+econ_stat_filters_applied_sentence+"*")

def click_apply_filter():
    apply_filters(input_start_date, input_end_date, input_interval, input_returninterval, equity_counter, debt_counter, econ_stat_counter, filtered_db_list, grammatical_selection)

if st.button("APPLY FILTERS", use_container_width=True, type="primary", key="apply_filters"):
    click_apply_filter()