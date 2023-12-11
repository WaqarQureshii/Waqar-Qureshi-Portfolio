import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import math
from datetime import datetime
import sys
from functools import reduce
sys.path.append("..")

st.set_page_config(layout="wide")

from functions.generate_db import *
from functions.last_business_date import *
from datetime import datetime

# -------- DATE SELECTION SECTION --------
    # --- DATE SELECTION ---
today_date = datetime.today()
header_col1, header_col2 = st.columns(2)
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

    # --- INDEX PARAMETERS
interval_selection = header_col2.radio("Select Interval",
                                       options =['Daily', 'Weekly', 'Monthly'],
                                       index = 0,
                                       key = "interval_selection")

if interval_selection == 'Daily':
    interval_input = '1d'
elif interval_selection == 'Weekly':
    interval_input = '1wk'
elif interval_selection == 'Monthly':
    interval_input = '1mo'


#Creating the sidebar with the different signal creations
st.sidebar.subheader("Select which signals you'd like to consider with WTDOLLE")
sidebar_counter = 0


# ------- SIDEBAR SELECTIONS ---------
    # --- VIX OPTIONS ---
vix_show = st.sidebar.checkbox("Volatility - VIX", value=True)
if vix_show == True:
        sidebar_counter += 1
        vix_show_label = st.sidebar.radio('Choose Signal Type',
                                ['VIX % Change' ,"VIX level"],
                                index=0)
        if vix_show_label == 'VIX level':
            vix_comparator_selection = st.sidebar.radio('Choose VIX comparator',
                                                      ['Greater than:', "Less than:"],
                                                      index = 1)
            vix_comparator_value = st.sidebar.text_input("input VIX integer (##)", 20)
            vix_comparator_value = int(vix_comparator_value)
        else:
            pass
else:
        pass
st.sidebar.divider()
    

    # --- HYG OPTIONS ---
hyg_show = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=True)
if hyg_show == True:
    sidebar_counter += 1
st.sidebar.divider()

    # --- RSI OPTIONS ---
rsi_show = st.sidebar.checkbox("Overbought / Oversold - S&P500 Relative Strength Index (RSI)", value=True)
if rsi_show == True:
    sidebar_counter += 1
    rsi_length = st.sidebar.text_input("Select the # of days for the RSI length", 10)

    rsi_comparator_selection = st.sidebar.radio('Choose RSI comparator',
                                                ['Greater than:', 'Less than:'],
                                                index = 1)
    rsi_comparator_value = st.sidebar.text_input("input RSI integer (##)", 20)
    rsi_comparator_value = int(rsi_comparator_value)
else:
     pass


st.sidebar.divider()

    # --- RSP OPTIONS ---
show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if show_rsp == True:
    rsp_ma_length = st.sidebar.text_input("Input Moving Average Length (days)", 50)
    rsp_ma_length = int(rsp_ma_length)
    sidebar_counter += 1
    rsp_comparator_selection = st.sidebar.radio('Choose RSP comparator',
                                                ['Price greater than MA', "Price less than MA"],
                                                index = 0)
else:
    pass
st.sidebar.divider()

    # --- YIELD CURVE ---
show_yieldcurve = st.sidebar.checkbox("US Yield Curve", value=False)
if show_yieldcurve == True:
    sidebar_counter += 1
    show_yield_option = st.sidebar.radio('3 month vs',
                                    ['10-year',
                                    '30-year'],
                                    index = 1)
st.sidebar.divider()        

# show_consumer = st.sidebar.checkbox("Consumer Index - XLY")
# if show_consumer == True:
#         sidebar_counter += 1

# show_utility = st.sidebar.checkbox("Utility (safe investment index) XLU")
# if show_utility == True:
#         sidebar_counter += 1

# show_ndxVSsp = st.sidebar.checkbox("Nasdaq vs S&P500 ratio", value=True)
# if show_ndxVSsp == True:
#         sidebar_counter += 1


# --- MAIN PAGE OF WTDOLLE - CHARTS AND PARAMETERS
    # -------------------- HEADER -------------------------
st.header(f'WTDOLLE on {input_end_date}')

st.text("")
st.text("")

    # ------------------ SUB HEADER -----------------------
if sidebar_counter == 0:
    st.header(f"{sidebar_counter} variables were selected in the sidebar")

elif sidebar_counter == 1:
    st.header(f"WTDOLLE with {sidebar_counter} selected variable")

else: st.subheader(f"WTDOLLE with the selected {sidebar_counter} variables")

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

# --- DATAFRAMES SET UP ---
# ---------- DATAFRAMES FOR COMMON DATE INDICES --------------
df_intersection = [] # TODO remove df_intersection once indices are set up.
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []
# --------------- DATAFRAMES FOR ALL INDICES ------------------
vix_metric = generate_vix(start_date, input_end_date, interval_input)
hyg_metric = generate_hyg(start_date, input_end_date, interval_input)
rsi_metric = sp500_rsi(start_date, input_end_date, int(rsi_length), interval_input)
rsp_metric = generate_rsp(start_date, input_end_date, interval_input, ma_length = rsp_ma_length)
sp500 = generate_sp500(start_date, input_end_date)
ndx = generate_ndx(start_date, input_end_date)


# ----- SELECTED VARIABLES COLUMNS ---------
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

# ------------------ ESTABLISH VIX CLOSING PRICE AND LAST % CHANGE FOR WTDOLLE ----------------------
with col1:
    if vix_show == True:
        
        vix_level = vix_metric["Close"].iloc[-1]
        str_vix_pct_change = "{:.2%}".format(vix_metric["% Change"].iloc[-1])
        int_vix_pct_change = vix_metric["% Change"].iloc[-1]


        if vix_show_label == "VIX % Change":
            st.metric(label = "VIX % Change", value = str_vix_pct_change)
            vix_pct_change_floor = math.floor(int_vix_pct_change*100)/100
            vix_pct_change_ceil = math.ceil(int_vix_pct_change*100)/100

            #Generate filtered dataset with selected parameters
            filtered_vix_metric = vix_metric[(vix_metric['% Change'] >= vix_pct_change_floor) & (vix_metric['% Change'] <= vix_pct_change_ceil)]
            df_intersection.append(filtered_vix_metric)
            sp500_intersection.append(filtered_vix_metric)
            nasdaq_intersection.append(filtered_vix_metric)
            rus2k_intersection.append(filtered_vix_metric)
        else:
            if vix_comparator_selection == 'Greater than:':
                vix_boolean = vix_level > vix_comparator_value
                st.metric(label=f'VIX > {vix_comparator_value}', value = f'{vix_boolean} @ {"{:.0f}".format(vix_level)}')
                filtered_vix_metric = vix_metric[vix_metric['Close'] > vix_comparator_value]
                df_intersection.append(filtered_vix_metric)
                sp500_intersection.append(filtered_vix_metric)
                nasdaq_intersection.append(filtered_vix_metric)
                rus2k_intersection.append(filtered_vix_metric)

            else:
                vix_boolean = vix_level < vix_comparator_value
                st.metric(label=f'VIX < {vix_comparator_value}', value = f'{vix_boolean} @ {"{:.0f}".format(vix_level)}')
                filtered_vix_metric = vix_metric[vix_metric['Close'] < vix_comparator_value]
                df_intersection.append(filtered_vix_metric)
                sp500_intersection.append(filtered_vix_metric)
                nasdaq_intersection.append(filtered_vix_metric)
                rus2k_intersection.append(filtered_vix_metric)

with col2:
     if hyg_show == True:

        #Grab the inputted end date's % Change
        str_hyg_pct_change = "{:.2%}".format(hyg_metric["% Change"].iloc[-1])
        int_hyg_pct_change = hyg_metric["% Change"].iloc[-1]
        hyg_pct_change_floor = math.floor(int_hyg_pct_change*100)/100
        hyg_pct_change_ceil = math.ceil(int_hyg_pct_change*100)/100

        #Generate filtered dataset with selected parameters
        filtered_hyg_metric = hyg_metric[(hyg_metric['% Change'] >= hyg_pct_change_floor) & (hyg_metric['% Change'] <= hyg_pct_change_ceil)]
        df_intersection.append(filtered_hyg_metric)
        sp500_intersection.append(filtered_hyg_metric)
        nasdaq_intersection.append(filtered_hyg_metric)
        rus2k_intersection.append(filtered_hyg_metric)

        #Show metric
        st.metric(label = "HYG % Change", value = str_hyg_pct_change)

with col3:
    if rsi_show == True:
        
        #Grab the inputted end date's metric
        rsi_level = rsi_metric["rsi"].iloc[-1]

        if rsi_comparator_selection == "Greater than:":
            rsi_boolean = rsi_level > rsi_comparator_value
            st.metric(label=f'RSI > {rsi_comparator_value}', value = f'{rsi_boolean} @ {"{:.0f}".format(rsi_level)}')

            #Generate filtered dataset with selected parameters
            filtered_rsi_metric = rsi_metric[rsi_metric['rsi'] > rsi_comparator_value]
            df_intersection.append(filtered_rsi_metric)
            sp500_intersection.append(filtered_hyg_metric)
            nasdaq_intersection.append(filtered_hyg_metric)
            rus2k_intersection.append(filtered_hyg_metric)

        else:
            rsi_boolean = rsi_level < rsi_comparator_value
            st.metric(label=f'RSI < {rsi_comparator_value}', value = f'{rsi_boolean} @ {"{:.0f}".format(rsi_level)}')

            #Generate filtered dataset with selected parameters
            filtered_rsi_metric = rsi_metric[rsi_metric['rsi'] < rsi_comparator_value]
            df_intersection.append(filtered_rsi_metric)
            sp500_intersection.append(filtered_hyg_metric)
            nasdaq_intersection.append(filtered_hyg_metric)
            rus2k_intersection.append(filtered_hyg_metric)

with col4:
    if show_rsp == True:

        #Grab inputted date's RSP Price and Moving Average
        rsp_price = rsp_metric["Close"].iloc[-1]
        rsp_ma = rsp_metric['ma'].iloc[-1]

        if rsp_comparator_selection == 'Price greater than MA':
            rsp_boolean = rsp_price > rsp_ma
            st.metric(label=f'Price > MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_boolean} @ {"{:.0f}".format(rsp_price)}')
            filtered_rsp_metric = rsp_metric[rsp_metric['Close'] > rsp_metric['ma']]
            df_intersection.append(filtered_rsp_metric)
            sp500_intersection.append(filtered_rsp_metric)
            nasdaq_intersection.append(filtered_rsp_metric)
            rus2k_intersection.append(filtered_rsp_metric)

        else:
            rsp_boolean = rsp_price < rsp_ma
            st.metric(label=f'Price < MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_boolean} @ {"{:.0f}".format(rsp_price)}')
            filtered_rsp_metric = rsp_metric[rsp_metric['Close'] < rsp_metric['ma']]
            df_intersection.append(filtered_rsp_metric)
            sp500_intersection.append(filtered_rsp_metric)
            nasdaq_intersection.append(filtered_rsp_metric)
            rus2k_intersection.append(filtered_rsp_metric)

st.write("")
st.write("")

# --------- PARAMETER SELECTIONS FOR INDIVIDUAL INDICES ---------
parameter_expander = st.expander("Choose additional parameters specific to each entity")
with parameter_expander:
    fig1, fig2, fig3 = st.columns(3)

# -------------------- S&P500 PARAMETER SELECTION ---------------------
    with fig1:
        st.subheader("S&P 500")
        fig1col1, fig1col2 = st.columns(2)
        with fig1col1:
            sp500_interval_selection = int(st.text_input("Calculate return over a selected # of intervals:", 10, key="sp500 interval selection"))
        with fig1col2:
            sp500rsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key="sp500 rsi indicator selection")
            if sp500rsishow == True:
                sp500comparator = st.radio('Choose comparator',
                                                      ['Greater than:', "Less than:"],
                                                      index = 1,
                                                      key = 'sp500 comparator selection')
                sp500_rsi_length = st.text_input("Select the RSI length (in intervals)", 10, key = "sp500 rsi length selector")

# -------------------------------- S&P500 DATAFRAME GENERATION -------------------------------
        sp500_index_columns = [df.index for df in df_intersection]
        sp500_common_index = reduce(lambda left, right: left.intersection(right), sp500_index_columns).to_list()

        # generates panda datafrane
        sp500['% Change Sel Interval'] = sp500['Close'].pct_change(sp500_interval_selection).shift(-sp500_interval_selection)

        sp500_common = sp500[sp500.index.isin(sp500_common_index)]

        fig, ax = plt.subplots()
        ax.set_title('S&P500')
        ax.plot(sp500.index, sp500['Close'], linewidth = 0.5, color='black')
        ax.scatter(sp500_common.index, sp500_common['Close'], marker='.', color='red', s = 10)
        st.pyplot(fig)
#--------------------------------------S&P500 GENERATE VALUES FOR STRING STATEMENTS-------------------------------
        average_sp500_return = sp500_common['% Change Sel Interval'].mean()
        sp500_number_of_occurrences = len(sp500_common['% Change Sel Interval'])
        sp500_number_of_positives = (sp500_common['% Change Sel Interval'] > 0).sum()
        sp500_positive_percentage = sp500_number_of_positives/sp500_number_of_occurrences
        sp500_positive_percentage = '{:.2%}'.format(sp500_positive_percentage)

        st.write(f'This occurred {sp500_number_of_occurrences} of time(s) and is {sp500_positive_percentage} positive in {sp500_interval_selection} days.' )
        st.write('{:.2%}'.format(average_sp500_return))

# -------------------- NASDAQ PARAMETER SELECTION ---------------------
    with fig2:
        st.subheader("Nasdaq")
        fig2col1, fig2col2 = st.columns(2)
        with fig2col1:
            nasdaq_interval_selection = int(st.text_input("Calculate return over a selected # of intervals:", 10, key="nasdaq interval selection"))
        with fig2col2:
            ndxrsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key="nasdaq rsi indicator selection")
            if ndxrsishow == True:
                nasdaqcomparator = st.radio('Choose comparator',
                                                      ['Greater than:', "Less than:"],
                                                      index = 1,
                                                      key = 'nasdaq comparator selection')
                nasdaq_rsi_length = st.text_input("Select the RSI length (in intervals)", 10, key = "nasdaq rsi length selector")
        
        # -------------------------------- NASDAQ DATAFRAME GENERATION -------------------------------
        index_columns = [df.index for df in df_intersection]
        common_index = reduce(lambda left, right: left.intersection(right), index_columns).to_list()

        ndx['% Change Sel Interval'] = ndx['Close'].pct_change(nasdaq_interval_selection).shift(-nasdaq_interval_selection)

        ndx_common = ndx[ndx.index.isin(common_index)]

        fig, ax = plt.subplots()
        ax.set_title('Nasdaq 100')
        ax.plot(ndx.index, ndx['Close'], linewidth = 0.5, color='black')
        ax.scatter(ndx_common.index, ndx_common['Close'], marker='.', color='red', s = 10)
        st.pyplot(fig)
#--------------------------------------NASDAQ GENERATE VALUES FOR STRING STATEMENTS-------------------------------
        average_ndx_return = ndx_common['% Change Sel Interval'].mean()
        ndx_number_of_occurrences = len(ndx_common['% Change Sel Interval'])
        ndx_number_of_positives = (ndx_common['% Change Sel Interval'] > 0).sum()
        ndx_positive_percentage = ndx_number_of_positives/ndx_number_of_occurrences
        ndx_positive_percentage = '{:.2%}'.format(ndx_positive_percentage)

        st.write(f'This occurred {ndx_number_of_occurrences} time(s) and is {ndx_positive_percentage} positive in {nasdaq_interval_selection} days.' )
        st.write('{:.2%}'.format(average_ndx_return))

# -------------------- RUS2K PARAMETER SELECTION ---------------------
    with fig3:
        st.subheader("Russel 2000")
        fig3col1, fig3col2 = st.columns(2)
        with fig3col1:
            rus2k_interval_selection = int(st.text_input("Calculate return over a selected # of intervals:", 10, key="rus2k interval selection"))
        with fig3col2:
            rus2krsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key="rus2k rsi indicator selection")
            if rus2krsishow == True:
                rus2kcomparator = st.radio('Choose comparator',
                                                      ['Greater than:', "Less than:"],
                                                      index = 1,
                                                      key = 'rus2k comparator selection')
                rus2k_rsi_length = st.text_input("Select the RSI length (in intervals)", 10, key = "rus2k rsi length selector")
        
# -------------------------------- RUSSEL 2000 DATAFRAME GENERATION -------------------------------
        index_columns = [df.index for df in df_intersection]
        common_index = reduce(lambda left, right: left.intersection(right), index_columns).to_list()

        # generates panda datafrane
        rus2k = generate_rus2k(start_date, input_end_date)
        rus2k['% Change Sel Interval'] = rus2k['Close'].pct_change(rus2k_interval_selection).shift(-rus2k_interval_selection)

        rus2k_common = rus2k[rus2k.index.isin(common_index)]

        fig, ax = plt.subplots()
        ax.set_title('Russel 2000')
        ax.plot(rus2k.index, rus2k['Close'], linewidth = 0.5, color='black')
        ax.scatter(rus2k_common.index, rus2k_common['Close'], marker='.', color='red', s = 10)
        st.pyplot(fig)
#--------------------------------------RUSSEL 2000 GENERATE VALUES FOR STRING STATEMENTS-------------------------------
        average_rus2k_return = rus2k_common['% Change Sel Interval'].mean()
        rus2k_number_of_occurrences = len(rus2k_common['% Change Sel Interval'])
        rus2k_number_of_positives = (rus2k_common['% Change Sel Interval'] > 0).sum()
        rus2k_positive_percentage = rus2k_number_of_positives/rus2k_number_of_occurrences
        rus2k_positive_percentage = '{:.2%}'.format(rus2k_positive_percentage)

        st.write(f'This occurred {rus2k_number_of_occurrences} of time(s) and is {rus2k_positive_percentage} positive in {rus2k_interval_selection} days.' )
        st.write('{:.2%}'.format(average_rus2k_return))