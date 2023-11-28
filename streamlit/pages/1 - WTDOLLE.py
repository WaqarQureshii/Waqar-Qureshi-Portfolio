import streamlit as st
import pandas as pd

import math
from datetime import datetime
import sys
sys.path.append("..")

st.set_page_config(layout="wide")

# from functions.generate_db import generate_vix, generate_hyg, generate_sp500
from functions.generate_db import *
from functions.last_business_date import *
from datetime import datetime

today_date = datetime.today()

input_end_date = st.date_input(label = 'Choose date', value = today_date)

#Creating the sidebar with the different signal creations
st.sidebar.subheader("Select which signals you'd like to consider with WTDOLLE")
sidebar_counter = 0

    #DISPLAY VIX OPTIONS
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
    

    #DISPLAY HYG OPTIONS
hyg_show = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=True)
if hyg_show == True:
    sidebar_counter += 1
st.sidebar.divider()

#DISPLAY RSI OPTIONS
rsi_show = st.sidebar.checkbox("Overbought / Oversold - Relative Strength Index (RSI)", value=True)
if rsi_show == True:
    sidebar_counter += 1
    rsi_length = st.sidebar.text_input("Select the # of days for the RSI length", 10)

    rsi_comparator_selection = st.sidebar.radio('Choose RSI comparator',
                                                ['Greater than:', 'Less than:'],
                                                index = 1)
    rsi_comparator_value = st.sidebar.text_input("input RSI integer (##)", 20)
else:
     pass


st.sidebar.divider()

#DISPLAY RSP OPTIONS
show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if show_rsp == True:
    sidebar_counter += 1
st.sidebar.divider()

#DISPLAY Yield Curve OPTIONS
show_yieldcurve = st.sidebar.checkbox("US Yield Curve", value=True)
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


#Main page of WTDOLLE
st.header(f'WTDOLLE on {input_end_date}')

st.text("")
st.text("")

start_date = '2001-01-01'
interval = "1d"

if sidebar_counter == 0:
    st.header(f"{sidebar_counter} variables were selected in the sidebar")

elif sidebar_counter == 1:
    st.header(f"WTDOLLE with {sidebar_counter} selected variable")

else: st.subheader(f"WTDOLLE with the selected {sidebar_counter} variables")

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

column_list = st.columns(sidebar_counter)
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

#Displaying VIX Column
with col1:
    if vix_show == True:
        #Generate entire VIX db with start, inputted end date and interval
        vix_metric = generate_vix(start_date, input_end_date, interval)
        
        #grab the closing price of the inputted end date
        vix_level = vix_metric["Close"].iloc[-1]

        #grab the inputted end date's % change
        str_vix_pct_change = "{:.2%}".format(vix_metric["% Change"].iloc[-1])
        vix_pct_change_int = vix_metric["% Change"].iloc[-1]*100

        if vix_show_label == "VIX % Change":
            st.metric(label = "VIX % Change", value = str_vix_pct_change)
            vix_pct_change_floor = math.floor(vix_pct_change_int)/100
            vix_pct_change_ciel = math.ceil(vix_pct_change_int)/100
            st.write(f'Floor: {vix_pct_change_floor}, Ciel: {vix_pct_change_ciel}')
        else:
            if vix_comparator_selection == 'Greater than:':
                vix_boolean = vix_level > vix_comparator_value
                st.metric(label=f'VIX @ {"{:.0f}".format(vix_level)}  > {vix_comparator_value}', value = vix_boolean)
                filtered_vix_metric = vix_metric[vix_metric['Close'] > vix_comparator_value]

            else:
                vix_boolean = vix_level < vix_comparator_value
                st.metric(label = f'VIX @ {"{:.0f}".format(vix_level)} < {vix_comparator_value}', value = vix_boolean)
                filtered_vix_metric = vix_metric[vix_metric['Close'] < vix_comparator_value]

with col2:
     if hyg_show == True:
        hyg_metric = generate_hyg(start_date, input_end_date, interval)
        hyg_pct_change = "{:.2%}".format(hyg_metric["% Change"].iloc[-1])

        st.metric(label = "HYG % Change", value = hyg_pct_change)

with col3:
    if rsi_show == True:
        rsi_metric = sp500_rsi(start_date, input_end_date, int(rsi_length), interval)
        rsi_level = rsi_metric["rsi"].iloc[-1]
        if rsi_comparator_selection == "Greater than:":
            rsi_boolean = rsi_level > int(rsi_comparator_value)
            st.metric(label=f'RSI @ {"{:.0f}".format(rsi_level)} > {rsi_comparator_value}', value = rsi_boolean)
        else:
            rsi_boolean = rsi_level < int(rsi_comparator_value)
            st.metric(label=f'RSI @ {"{:.0f}".format(rsi_level)} < {rsi_comparator_value}', value = rsi_boolean)

