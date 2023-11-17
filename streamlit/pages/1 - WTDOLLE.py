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
column_list = []

    #DISPLAY VIX OPTIONS
show_vix = st.sidebar.checkbox("Volatility - VIX", value=True)
if show_vix == True:
        column_list.append("col1")
        sidebar_counter += 1
        show_vix_label = st.sidebar.radio('Choose Signal Type',
                                ['VIX % Change' ,"VIX level"],
                                index=0)
        if show_vix_label == 'VIX level':
            show_vix_label = st.sidebar.text_input("input (<#) or (>#) text", "<20")
        else:
            pass
else:
        pass
st.sidebar.divider()
    

    #DISPLAY HYG OPTIONS
show_hyg = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=True)
if show_hyg == True:
    sidebar_counter += 1
    column_list.append("col2")
st.sidebar.divider()

#DISPLAY RSI OPTIONS
show_rsi = st.sidebar.checkbox("Overbought / Oversold - Relative Strength Index (RSI)", value=True)
if show_rsi == True:
    sidebar_counter += 1
    column_list.append("col3")
st.sidebar.divider()

#DISPLAY RSP OPTIONS
show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if show_rsp == True:
    sidebar_counter += 1
    column_list.append("col4")
st.sidebar.divider()

#DISPLAY Yield Curve OPTIONS
show_yieldcurve = st.sidebar.checkbox("US Yield Curve", value=True)
if show_yieldcurve == True:
    column_list.append("col5")
    sidebar_counter += 1
    show_yield_option = st.sidebar.radio('3 month vs',
                                    ['10-year',
                                    '30-year'],
                                    index = 1)
st.sidebar.divider()        

show_consumer = st.sidebar.checkbox("Consumer Index - XLY")
if show_consumer == True:
        column_list.append("col6")
        sidebar_counter += 1

show_utility = st.sidebar.checkbox("Utility (safe investment index) XLU")
if show_utility == True:
        column_list.append("col7")
        sidebar_counter += 1

show_ndxVSsp = st.sidebar.checkbox("Nasdaq vs S&P500 ratio", value=True)
if show_ndxVSsp == True:
        column_list.append("col8")
        sidebar_counter += 1


#Main page of WTDOLLE
st.write('''
# WTDOLLE
## This is what happened today with the variables selected on the sidebar:
''')

st.text("")
st.text("")

if sidebar_counter == 0:
    st.header(f"{sidebar_counter} variables were selected in the sidebar")

elif sidebar_counter == 1:
    st.header(f"WTDOLLE with {sidebar_counter} selected variable")

else: st.header(f"WTDOLLE with the selected {sidebar_counter} variables")


column_list = st.columns(sidebar_counter)

if show_vix == True:
      if show_vix_label == "VIX level":
            col1.write("v")

# with st.expander("Variables to include/exclude (select):"):
#     col1, col2, col3, col4, col5, col6, col7, col8= st.columns(8)
#     with col1:
#         st.write("Volatility Index")
        
#         show_vix = st.checkbox('VIX', value=True)
#         if show_vix == True:
#             show_vix_label = st.radio('Choose Signal Type',
#                                     ['VIX % Change' ,"VIX level"],
#                                     index=0)
#         else:
#             pass

#     with col2:
#         st.write("Junk Bonds")
#         show_hyg = st.checkbox('HYG', value=True)
        
#     with col3:
#         st.write("Overbought / Oversold")
#         show_rsi = st.checkbox("RSI", value=True)
#         if show_rsi == True:
#             show_rsi_label = st.text_input("RSI metric", "<20")
#         else:
#             pass

#     with col4:
#         st.write("Market Thrust")
#         show_rsp = st.checkbox("RSP")

#     with col5:
#         st.write("Yield Curve")
#         show_yield = st.checkbox("Yield Curve", value=True)
#         if show_yield == True:
#             show_yield_label = st.radio('3-month vs ',
#                                     ["10-year", "30-year"],
#                                     index=1)

#             show_yield_metric = st.radio('Choose Yield Metric:',
#                                          ['Yield Curve % Change',
#                                           'Yield Curve Value'])
#         else:
#             pass

#     with col6:
#         st.write("Consumer")
#         show_consumer = st.checkbox("XLY")

#     with col7:
#         st.write("Utility")
#         show_consumer = st.checkbox("XLU")

#     with col8:
#         st.write("Nasdaq vs SP500 Ratio")
#         show_ndxVSsp = st.checkbox("NDX vs SP500")
#         if show_ndxVSsp == True:
#             show_ndxVSsp_label = st.radio('NDX vs SP500',
#                                           ['% Change',
#                                            'Ratio'])