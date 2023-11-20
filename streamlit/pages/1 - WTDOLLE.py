import streamlit as st
import pandas as pd
from datetime import datetime

import sys
sys.path.append("..")

st.set_page_config(layout="wide")

from functions.generate_db import generate_vix


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
            vix_comparator_selection = st.sidebar.radio('Choose comparator',
                                                      ['Greater than:', "Less than:"],
                                                      )
            vix_comparator_value = st.sidebar.text_input("input integer (##)", "20")
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
show_rsi = st.sidebar.checkbox("Overbought / Oversold - Relative Strength Index (RSI)", value=True)
if show_rsi == True:
    sidebar_counter += 1
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

show_consumer = st.sidebar.checkbox("Consumer Index - XLY")
if show_consumer == True:
        sidebar_counter += 1

show_utility = st.sidebar.checkbox("Utility (safe investment index) XLU")
if show_utility == True:
        sidebar_counter += 1

show_ndxVSsp = st.sidebar.checkbox("Nasdaq vs S&P500 ratio", value=True)
if show_ndxVSsp == True:
        sidebar_counter += 1


#Main page of WTDOLLE
st.write('''
# WTDOLLE
## This is what happened today with the variables selected on the sidebar:
''')

st.text("")
st.text("")

start_date = '2001-01-01'
default_end_date = '2023-11-18'
interval = "1d"

if sidebar_counter == 0:
    st.header(f"{sidebar_counter} variables were selected in the sidebar")

elif sidebar_counter == 1:
    st.header(f"WTDOLLE with {sidebar_counter} selected variable")

else: st.header(f"WTDOLLE with the selected {sidebar_counter} variables")

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 25px;
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
        vix_metric = generate_vix(start_date, default_end_date, interval)
        # vix_metrix_lastday = 
        if vix_show_label == "VIX % Change":
            vix_pct_change = "{:.2%}".format(vix_metric["% Change"].iloc[-1])
            st.metric(label = "VIX % Change", value = vix_pct_change)
        else:
            vix_level = vix_metric["Close"].iloc[-1]

            if vix_comparator_selection == 'Greater than:':
                vix_metric_value = vix_level > int(vix_comparator_value)
                st.metric(label=f'VIX @ {"{:.0f}".format(   )}  > {vix_comparator_value}', value = vix_metric_value)

            else:
                vix_metric_value = vix_level < int(vix_comparator_value)
                st.metric(label = f'VIX @ {"{:.0f}".format(vix_level)} < {vix_comparator_value}', value = vix_metric_value)


with col2:
     