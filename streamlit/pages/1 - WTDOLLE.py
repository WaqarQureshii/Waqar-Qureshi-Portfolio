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

st.set_page_config(layout="wide")

# -------- DATE SELECTION SECTION --------
    # --- DATE SELECTION ---
today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
header_col1, header_col2 = st.columns(2)
input_start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

    # --- INDEX PARAMETERS
selection_interval = header_col2.radio("Select Interval",
                                       options =['Daily', 'Weekly', 'Monthly'],
                                       index = 0,
                                       key = "interval_selection")

if selection_interval == 'Daily':
    interval_input = '1d'
    grammatical_selection = 'days'
elif selection_interval == 'Weekly':
    interval_input = '1wk'
    grammatical_selection = 'weeks'
elif selection_interval == 'Monthly':
    interval_input = '1mo'
    grammatical_selection = 'months'


#Creating the sidebar with the different signal creations
st.sidebar.subheader("Global Parameters used with WTDOLLE")
sidebar_counter = 0

# --- Dataframes Set Up ---
# ---------- DATAFRAMES FOR COMMON DATE INDICES --------------
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []

# --- SELECTED VARIABLES COLUMNS ---
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

# ------- SIDEBAR SELECTIONS ---------
    # --- VIX OPTIONS ---
header_show_vix = st.sidebar.checkbox("Volatility - VIX", value=True)
if header_show_vix == True:
# --- VIX UI ---
# --- VIX Database Generation ---
    sidebar_counter += 1
    db_vix, current_value_vix, current_pct_vix_str, current_pct_vix_int, current_pct_floor_vix, current_pct_ceiling_vix = generate_vix(input_start_date, input_end_date, interval_input)

    selected_signal_vix = st.sidebar.radio('Choose Signal Type',
                            [f'VIX % Change: {current_pct_vix_str}' ,f'VIX level: {round(current_value_vix,1)}'],
                            index=0)

    if selected_signal_vix == f'VIX level: {round(current_value_vix,1)}':
# ------ VIX UI for VIX level selection ------
        subheader_comparator_vix = st.sidebar.radio('Choose VIX comparator',
                                                    ['Greater than', "Less than"],
                                                    index = 1,
                                                    key = "comparator vix level selector")
        selected_value_vix = int(st.sidebar.text_input("Input VIX integer (##)", value = int(current_value_vix+1))) #TODO add intelligent default values

        if subheader_comparator_vix == 'Greater than':
            boolean_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_level_greater_than(current_value_vix, selected_value_vix, db_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col1.metric(label=f'VIX > {selected_value_vix}', value = f'{boolean_vix} @ {"{:.0f}".format(current_value_vix)}')

        else:
            boolean_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_level_lower_than(current_value_vix, selected_value_vix, db_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col1.metric(label=f'VIX < {selected_value_vix}', value = f'{boolean_vix} @ {"{:.0f}".format(current_value_vix)}')
        
        col1.line_chart(db_vix['Close'], height = 100, use_container_width = True)

# ------ VIX UI for VIX % Change Selection ------
    else:
        subheader_comparator_vix = st.sidebar.radio('Choose VIX comparator',
        ['Greater than', "Less than"],
        index = 1, key = "comparator vix pct selector")
        selected_pct_change = float(st.sidebar.text_input("Input percent increase/decrease", value = 
        current_pct_ceiling_vix*100, key = 'VIX pct comparator value'))
        
        if subheader_comparator_vix == 'Greater than':
            boolean_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_pct_change_manual(db_vix, subheader_comparator_vix, selected_pct_change, current_pct_vix_int, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col1.metric(label = f"VIX % > {selected_pct_change}", value = f'{boolean_vix} @ {current_pct_vix_str}')
        else:
            boolean_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_pct_change_manual(db_vix, subheader_comparator_vix, selected_pct_change, current_pct_vix_int, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col1.metric(label = f"VIX % < {selected_pct_change}", value = f'{boolean_vix} @ {current_pct_vix_str}')
        
        col1.line_chart(db_vix['% Change']*100, height = 100, use_container_width = True)
else:
    pass
st.sidebar.divider()

    # --- HYG OPTIONS ---
header_show_hyg = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=False)
if header_show_hyg == True:
    sidebar_counter += 1

    db_hyg, current_pct_hyg_str, current_pct_hyg_int, current_pct_floor_hyg, current_pct_ceiling_hyg = generate_hyg(input_start_date, input_end_date, interval_input)

    subheader_comparator_hyg = st.sidebar.radio('Choose HYG comparator',
    ['Greater than', "Less than"],
    index = 1, key = "comparator hyg pct selector")
    selected_pct_change = float(st.sidebar.text_input("Input percent increase/decrease", value = 
    current_pct_ceiling_hyg*100, key = 'HYG pct comparator value'))
    
    if subheader_comparator_hyg == 'Greater than':
        boolean_hyg, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_pct_change_manual(db_hyg, subheader_comparator_hyg, selected_pct_change, current_pct_hyg_int, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        col2.metric(label = f"HYG % > {selected_pct_change}", value = f'{boolean_hyg} @ {current_pct_hyg_str}')
    else:
        boolean_hyg, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_pct_change_manual(db_hyg, subheader_comparator_hyg, selected_pct_change, current_pct_hyg_int, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        col2.metric(label = f"HYG % < {selected_pct_change}", value = f'{boolean_hyg} @ {current_pct_hyg_str}')
    
    col2.line_chart(db_hyg['% Change']*100, height = 100, use_container_width = True)

st.sidebar.divider()

    # --- RSP OPTIONS ---
header_show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if header_show_rsp == True:
    rspMAorRSI = st.sidebar.multiselect('Choose your RSP parameters', ['Moving Average (MA)', 'RSI (Relative Strength Index)'])
    st.sidebar.write("")
    
    if 'Moving Average (MA)' in rspMAorRSI and 'RSI (Relative Strength Index)' in rspMAorRSI:
        st.sidebar.subheader('RSP Moving Average') #---MOVING AVERAGE SECTION---

        sidebar_counter += 2
        rsp_ma_length = int(st.sidebar.text_input("Input Moving Average Length (interval)", 50, key='rsp ma length'))
        rsp_macomparator_selection = st.sidebar.radio('Choose RSP comparator',
                                                    ['Price greater than MA', "Price less than MA"],
                                                    index = 0)
        
        st.sidebar.write("")

        st.sidebar.subheader('RSP RSI') #---RSI SECTION ---
        rsp_rsi_length = int(st.sidebar.text_input('Input RSI length', 22, key = 'rsp rsi length'))
        rsp_rsi_comparator = st.sidebar.radio('Choose RSP RSI comparator',
                                            ['Greater than', 'Less than'],
                                            index=0,
                                            key = 'rsp rsi comparator')
        rsp_rsi_value_selection = int(st.sidebar.text_input("Input RSI value to compare against",
                                              70,
                                              key='rsp rsi value selection'))
        #---database generator---
        db_rsp, rsp_price, rsp_ma, rsp_rsi_current_value = generate_rsp(input_start_date, input_end_date, interval_input, ma_length = rsp_ma_length, rsi_value = rsp_rsi_length)
        #---database generator---
        
        if rsp_macomparator_selection == "Price greater than MA": #---Moving Average Signal generator---
            rsp_ma_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_p_greater_than_MA(db_rsp, rsp_price, rsp_ma, sp500_intersection, nasdaq_intersection, rus2k_intersection)  
            col3.metric(label=f'Price > {rsp_ma_length} day MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_ma_boolean} @ {"{:.0f}".format(rsp_price)}')
        else:
            rsp_ma_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_p_lower_than_MA(db_rsp, rsp_price, rsp_ma, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col3.metric(label=f'Price < {rsp_ma_length} day MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_ma_boolean} @ {"{:.0f}".format(rsp_price)}')

        if rsp_rsi_comparator == 'Greater than': #---RSI Signal generator---
            rsp_rsi_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_rsi_greater_than(db_rsp, rsp_rsi_current_value, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col4.metric(label=f'RSP {rsp_rsi_length} day RSI > {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_current_value)}')
        else:
            rsp_rsi_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_rsi_lower_than(db_rsp, rsp_rsi_current_value, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col4.metric(label=f'RSP {rsp_rsi_length} day RSI < {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_current_value)}')
        
        col3.line_chart(db_rsp['ma'], height = 100, use_container_width = True)
        col4.line_chart(db_rsp['rsi'], height = 100, use_container_width = True)

    elif 'Moving Average (MA)' in rspMAorRSI:
        st.sidebar.subheader('RSP Moving Average')

        sidebar_counter += 1
        rsp_ma_length = int(st.sidebar.text_input("Input Moving Average Length (interval)", 50, key='rsp ma length'))
        
        db_rsp, rsp_price, rsp_ma, rsp_rsi_current_value = generate_rsp(input_start_date, input_end_date, interval_input, ma_length = rsp_ma_length)

        rsp_comparator_selection = st.sidebar.radio('Choose RSP comparator',
                                                    ['Price greater than MA', "Price less than MA"],
                                                    index = 0)
        
        if rsp_comparator_selection == "Price greater than MA":
            rsp_ma_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_p_greater_than_MA(db_rsp, rsp_price, rsp_ma, sp500_intersection, nasdaq_intersection, rus2k_intersection)  
            col3.metric(label=f'Price > ({rsp_ma_length}) MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_ma_boolean} @ {"{:.0f}".format(rsp_price)}')
        else:
            rsp_ma_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_p_lower_than_MA(db_rsp, rsp_price, rsp_ma, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col3.metric(label=f'Price < ({rsp_ma_length}) MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_ma_boolean} @ {"{:.0f}".format(rsp_price)}')

        col3.line_chart(db_rsp['ma'], height = 100, use_container_width = True)

        st.sidebar.write("")
    
    elif 'RSI (Relative Strength Index)' in rspMAorRSI:
        st.sidebar.subheader('RSP RSI')
        rsp_rsi_length = int(st.sidebar.text_input('Input RSI length', 22, key = 'rsp rsi length'))

        sidebar_counter += 1
        db_rsp, rsp_price, rsp_ma, rsp_rsi_current_value = generate_rsp(input_start_date, input_end_date, interval_input, rsi_value = rsp_rsi_length)
        
        rsp_rsi_comparator = st.sidebar.radio('Choose RSP RSI comparator',
                                            ['Greater than', 'Less than'],
                                            index=0,
                                            key = 'rsp rsi comparator')

        rsp_rsi_value_selection = int(st.sidebar.text_input("Input RSI value to compare against",
                                              70,
                                              key='rsp rsi value selection'))
        
        if rsp_rsi_comparator == 'Greater than': #---RSI Signal generator---
            rsp_rsi_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_rsi_greater_than(db_rsp, rsp_rsi_current_value, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col4.metric(label=f'RSP ({rsp_rsi_length}) RSI > {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_current_value)}')
        else:
            rsp_rsi_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_rsi_lower_than(db_rsp, rsp_rsi_current_value, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col4.metric(label=f'RSP ({rsp_rsi_length}) RSI < {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_current_value)}')   
        
        col4.line_chart(db_rsp['rsi'], height = 100, use_container_width = True)

else:
    pass
st.sidebar.divider()

    # --- YIELD CURVE ---
show_yieldcurve = st.sidebar.checkbox("US Yield Curve", value=False, key='show yield curve')
if show_yieldcurve == True:
    sidebar_counter += 1
    show_yield_option = st.sidebar.radio('3 month vs',
                                    ['10-year',
                                    '30-year'],
                                    index = 1,
                                    key = 'show yield option')
    yieldcurve_comparator_selection = st.sidebar.radio('Choose Yield Curve comparator',
                                                       ['Diff greater than', 'Diff less than'],
                                                       index = 0)
    selected_yieldcurve_diff = float(st.sidebar.text_input("Input Yield Diff to compare",
                                                 0.5,
                                                 key = 'Yield Curve level'))
    
    if show_yield_option == '30-year':
        yielddiff, curr_yielddiff, curr_ltyield, curr_styield = yield_diff(input_start_date,
                                        input_end_date,
                                        lt_yield_inp='30y')
        
        if yieldcurve_comparator_selection == "Diff greater than": # Current Yield Curve greater than Selected Difference Value
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_greater(yielddiff, curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff > {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {curr_yielddiff}')
        
        else: # Current Yield Curve less than Selected Difference Value
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_lower(yielddiff, curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff < {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {curr_yielddiff}')
    
    else:
        yielddiff, curr_yielddiff, curr_ltyield, curr_styield = yield_diff(input_start_date,
                                        input_end_date,
                                        lt_yield_inp='10y')
        
        if yieldcurve_comparator_selection == "Diff greater than":
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_greater(yielddiff, curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff > {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {curr_yielddiff}')

        else:
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_lower(yielddiff, curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff < {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {curr_yielddiff}')


    col5.line_chart(yielddiff['Yield Diff'],
                    use_container_width = True,
                    height = 100)
    
st.sidebar.divider()        

#NASDAQ vs SP500 RATIO
header_show_ndxvssp500 = st.sidebar.checkbox("Nasdaq vs SP500 Ratio", value = False, key = "show Nasdaq vs SP500")
if header_show_ndxvssp500:
    sidebar_counter += 1
    selected_signal_ndxvssp500 = st.sidebar.radio('Evaluate',
                                            ['Nasdaq vs SP500 Ratio', 'Nasdaq vs SP500 Ratio % Change'],
                                            index=0)
    
    if selected_signal_ndxvssp500 == 'Nasdaq vs SP500 Ratio':
        selected_comparator_ndxsp500 = st.sidebar.radio('Choose comparator',
                                                         ['Greater than', 'Lower than'],
                                                         index = 0, key = 'ndx vs SP500 Comparator Selection')
        selected_ratio_value_ndxsp500 = float(st.sidebar.text_input("Input Nasdaq vs SP500 ratio to compare against",
                                                           1,
                                                           key = 'Nasdaq vs Sp500 Ratio Level'))
        
        db_ndxsp500, current_ratio_ndxsp500, current_ratio_pct_ndxsp500, current_ratio_pct_ndxsp500_str, nasdaq, sp500 = nasdaqvssp500(input_start_date, input_end_date, interval_input)

        if selected_comparator_ndxsp500 == 'Greater than': #LEVEL - Greater than
            ndxsp500_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_value(db_ndxsp500, selected_comparator_ndxsp500, current_ratio_ndxsp500, selected_ratio_value_ndxsp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col6.metric(label=f'NDX/SPY > {selected_ratio_value_ndxsp500}', value = f'{ndxsp500_boolean} @ {round(current_ratio_ndxsp500,2)}')

        elif selected_comparator_ndxsp500 == 'Lower than': #LEVEL - Lower than
            ndxsp500_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_value(db_ndxsp500, selected_comparator_ndxsp500, current_ratio_ndxsp500, selected_ratio_value_ndxsp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col6.metric(label=f'NDX/SPY < {selected_ratio_value_ndxsp500}', value = f'{ndxsp500_boolean} @ {round(current_ratio_ndxsp500,2)}')
        
        col6.line_chart(db_ndxsp500['Ratio'], use_container_width = True, height = 100)

    elif selected_signal_ndxvssp500 == 'Nasdaq vs SP500 Ratio % Change':
        selected_comparator_ndxsp500 = st.sidebar.radio('Choose comparator',
                                                         ['Greater than', 'Lower than'],
                                                         index = 0, key = 'ndx vs SP500 Comparator Selection')
        ndxsp500_ratio_pct_selected = float(st.sidebar.text_input("Input Nasdaq vs SP500 Ratio % Change to compare against", 1.2, key = 'Nasdaq vs Sp500 Ratio Level % Change'))

        db_ndxsp500, curr_ndxsp500_ratio, current_ratio_pct_ndxsp500, current_ratio_pct_ndxsp500_str, nasdaq, sp500 = nasdaqvssp500(input_start_date, input_end_date, interval_input)

        if selected_comparator_ndxsp500 == 'Greater than': #% Change - Greater than
            ndxsp500_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_pct_value(db_ndxsp500, selected_comparator_ndxsp500, current_ratio_pct_ndxsp500, ndxsp500_ratio_pct_selected, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col6.metric(label=f'NDX/SPY % Chg > {ndxsp500_ratio_pct_selected}', value = f'{ndxsp500_boolean} @ {current_ratio_pct_ndxsp500}')

        elif selected_comparator_ndxsp500 == 'Lower than': #% Change - Lower than
            ndxsp500_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_pct_value(db_ndxsp500, selected_comparator_ndxsp500, current_ratio_pct_ndxsp500, ndxsp500_ratio_pct_selected, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col6.metric(label=f'NDX/SPY % Chg < {ndxsp500_ratio_pct_selected}', value = f'{ndxsp500_boolean} @ {current_ratio_pct_ndxsp500_str}')
    
        col6.line_chart(db_ndxsp500['Ratio % Chg'], use_container_width = True, height = 100)

st.sidebar.divider()

#Russel 2000 vs SP500 RATIO
header_show_rus2ksp500 = st.sidebar.checkbox("Russel 2000 vs SP500 Ratio", value = False, key = "show Russ2k vs SP500")
if header_show_rus2ksp500:
    sidebar_counter += 1
    selected_signal_rus2ksp500 = st.sidebar.radio('Evaluate',
                                            ['Russell 2000 vs SP500 Ratio', 'Russell 2000 vs SP500 Ratio % Change'],
                                            index=0)
    
    if selected_signal_rus2ksp500 == 'Russell 2000 vs SP500 Ratio':
        selected_comparator_rus2ksp500 = st.sidebar.radio('Choose comparator',
                                                         ['Greater than', 'Lower than'],
                                                         index = 0, key = 'rus2k vs SP500 Comparator Selection')
        selected_ratio_rus2ksp500 = float(st.sidebar.text_input("Input Russell 2000 vs SP500 ratio to compare against",
                                                           1,
                                                           key = 'Russell 2000 vs Sp500 Ratio Level'))
        
        db_rus2ksp500, current_ratio_rus2ksp500, current_ratio_pct_rus2ksp500, current_ratio_pct_str_rus2ksp500, rus2k, sp500 = rus2kvssp500(input_start_date, input_end_date, interval_input)

        if selected_comparator_rus2ksp500 == 'Greater than': #LEVEL - Greater than
            boolean_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_value(db_rus2ksp500, selected_comparator_rus2ksp500, current_ratio_rus2ksp500, selected_ratio_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col7.metric(label=f'Rus2k/SPY > {selected_ratio_rus2ksp500}', value = f'{boolean_rus2ksp500} @ {round(current_ratio_rus2ksp500,2)}')

        elif selected_comparator_rus2ksp500 == 'Lower than': #LEVEL - Lower than
            boolean_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_value(db_rus2ksp500, selected_comparator_rus2ksp500, current_ratio_rus2ksp500, selected_ratio_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col7.metric(label=f'Rus2k/SPY < {selected_ratio_rus2ksp500}', value = f'{boolean_rus2ksp500} @ {round(current_ratio_rus2ksp500,2)}')
        
        col7.line_chart(db_rus2ksp500['Ratio'], use_container_width = True, height = 100)

    elif selected_signal_rus2ksp500 == 'Russell 2000 vs SP500 Ratio % Change':
        selected_comparator_rus2ksp500 = st.sidebar.radio('Choose comparator',
                                                         ['Greater than', 'Lower than'],
                                                         index = 0, key = 'rus2k vs SP500 Comparator Selection')
        selected_ratio_pct_rus2ksp500 = float(st.sidebar.text_input("Input Russell 2000 vs SP500 Ratio % Change to compare against", 1.2, key = 'Russell 2000 vs Sp500 Ratio Level % Change'))

        db_rus2ksp500, current_ratio_rus2ksp500, current_ratio_pct_rus2ksp500, current_ratio_pct_str_rus2ksp500, rus2k, sp500 = rus2kvssp500(input_start_date, input_end_date, interval_input)

        if selected_comparator_rus2ksp500 == 'Greater than': #% Change - Greater than
            boolean_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_pct_value(db_rus2ksp500, selected_comparator_rus2ksp500, current_ratio_pct_rus2ksp500, selected_ratio_pct_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col7.metric(label=f'NDX/SPY % Chg > {selected_ratio_pct_rus2ksp500}', value = f'{boolean_rus2ksp500} @ {current_ratio_pct_rus2ksp500}')

        elif selected_comparator_rus2ksp500 == 'Lower than': #% Change - Lower than
            boolean_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection = signal_ratio_pct_value(db_rus2ksp500, selected_comparator_rus2ksp500, current_ratio_pct_rus2ksp500, selected_ratio_pct_rus2ksp500, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col7.metric(label=f'Rus2k/SPY % Chg < {selected_ratio_pct_rus2ksp500}', value = f'{boolean_rus2ksp500} @ {current_ratio_pct_str_rus2ksp500}')
    
        col7.line_chart(db_rus2ksp500['Ratio % Chg'], use_container_width = True, height = 100)

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
            sp500, sp500rsicurrent = generate_sp500(input_start_date, input_end_date, interval=interval_input, rsi_value=sp500_rsi_length)

            sp500comparator = st.radio(f'Choose comparator, current RSI {sp500rsicurrent}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="sp500 RSI comparator")
            sp500rsivalue = int(st.text_input('Input RSI value',
                                              sp500rsicurrent - 1,
                                              key="sp500rsivalue"))

            if sp500comparator == 'Greater than':
                filtered_sp500rsi_metric = sp500[sp500['rsi'] > sp500rsivalue]
                sp500_intersection.append(filtered_sp500rsi_metric)
            else:
                filtered_sp500rsi_metric = sp500[sp500['rsi'] < sp500rsivalue]
                sp500_intersection.append(filtered_sp500rsi_metric)
        else:
            sp500, sp500rsicurrent = generate_sp500(input_start_date, input_end_date, interval=interval_input)

col2.subheader("Nasdaq")
with col2.expander("Nasdaq Parameter Section"):
    ndxcol1, ndxcol2 = st.columns(2)
    with ndxcol1:
        ndx_return_interval = int(st.text_input(f"# of {grammatical_selection} to calculate return over", 10, key="ndx return interval"))
    with ndxcol2:
        ndxrsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='ndx RSI show')
        if ndxrsishow:
            ndx_rsi_length = int(st.text_input('Select RSI length (in intervals)', 22, key = "ndx RSI length"))
            ndx, ndxrsicurrent = generate_ndx(input_start_date, input_end_date, interval=interval_input, rsi_value=ndx_rsi_length)
            ndxcomparator = st.radio(f'Choose comparator, current RSI {ndxrsicurrent}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="ndx RSI comparator")
            ndxrsivalue = int(st.text_input('Input RSI value',
                                            ndxrsicurrent - 1,
                                            key="ndxrsivalue"))
            
            if ndxcomparator =='Greater than':
                filtered_ndxrsi_metric = ndx[ndx['rsi'] > ndxrsivalue]
                nasdaq_intersection.append(filtered_ndxrsi_metric)
            else:
                filtered_ndxrsi_metric = ndx[ndx['rsi'] < ndxrsivalue]
                nasdaq_intersection.append(filtered_ndxrsi_metric)
        else:
            ndx, ndxrsicurrent = generate_ndx(input_start_date, input_end_date, interval=interval_input)

col3.subheader("Russell 2000")
with col3.expander("Russell 2000 Parameter Section"):
    rus2kcol1, rus2kcol2 = st.columns(2)
    with rus2kcol1:
        rus2k_return_interval = int(st.text_input(f"# of {grammatical_selection} to calculate return over", 10, key="rus2k return interval"))
    with rus2kcol2:
        rus2krsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='rus2k RSI show')
        if rus2krsishow:
            rus2k_rsi_length = int(st.text_input('Select RSI lenght (in intervals)', 22, key = "rus2k RSI length"))
            rus2k, rus2krsicurrent = generate_rus2k(input_start_date, input_end_date, interval=interval_input, rsi_value=rus2k_rsi_length)
            rus2kcomparator = st.radio(f'Choose comparator, current RSI {rus2krsicurrent}',
                                       ['Greater than', 'Lower than'],
                                       index = 0,
                                       key="rus2k RSI comparator")
            rus2krsivalue = int(st.text_input('Input RSI value',
                                            rus2krsicurrent - 1,
                                            key='rus2krsivalue'))
            
            if rus2kcomparator == 'Greater than':
                filtered_rus2krsi_metric = rus2k[rus2k['rsi'] > rus2krsivalue]
                rus2k_intersection.append(filtered_rus2krsi_metric)

            else:
                filtered_rus2krsi_metric = rus2k[rus2k['rsi'] < rus2krsivalue]
                rus2k_intersection.append(filtered_rus2krsi_metric)
        else:
            rus2k, rus2krsicurrent = generate_rus2k(input_start_date, input_end_date, interval=interval_input)

# --- Indices Generation ---
if sidebar_counter > 0:
    #---S&P500 DATABASE GENERATION---
    db_filtered_sp500, avg_sp500_return, no_of_occurrences_sp500, positive_percentage_sp500 = signal_pct_positive(sp500, sp500_intersection, sp500_return_interval)
    #-------S&P500 GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('S&P500')
    ax.plot(sp500.index, sp500['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_sp500.index, db_filtered_sp500['Close'], marker='.', color='red', s = 10)
    graph1.pyplot(fig)
    #-------S&P500 GENERATE STATEMENTS--------
    graph1.write(f'This occurred {no_of_occurrences_sp500} of time(s) and is {positive_percentage_sp500} positive in {sp500_return_interval} days.' )
    graph1.write('{:.2%}'.format(avg_sp500_return))

    #---NASDAQ DATABASE GENERATION---
    db_filtered_ndx, avg_ndx_return, no_of_occurrences_ndx, positive_percentage_ndx = signal_pct_positive(ndx, nasdaq_intersection, ndx_return_interval)
    #-------NASDAQ GRAPH------
    fig, ax = plt.subplots()
    ax.set_title('Nasdaq 100')
    ax.plot(ndx.index, ndx['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_ndx.index, db_filtered_ndx['Close'], marker='.', color='red', s = 10)
    graph2.pyplot(fig)
    #-------NASDAQ GENERATE STATEMENTS-------
    graph2.write(f'This occurred {no_of_occurrences_ndx} time(s) and is {positive_percentage_ndx} positive in {ndx_return_interval} days.' )
    graph2.write('{:.2%}'.format(avg_ndx_return))

    #--RUSSEL 2000 DATABASE GENERATION
    db_filtered_rus2k, avg_rus2k_return, no_of_occurrences_rus2k, positive_percentage_rus2k = signal_pct_positive(rus2k, rus2k_intersection, rus2k_return_interval)
    #-----RUSSELL 2000 GRAPH-----
    fig, ax = plt.subplots()
    ax.set_title('Russel 2000')
    ax.plot(rus2k.index, rus2k['Close'], linewidth = 0.5, color='black')
    ax.scatter(db_filtered_rus2k.index, db_filtered_rus2k['Close'], marker='.', color='red', s = 10)
    graph3.pyplot(fig)
    #-------NASDAQ GENERATE STATEMENTS-------
    graph3.write(f'This occurred {no_of_occurrences_rus2k} of time(s) and is {positive_percentage_rus2k} positive in {rus2k_return_interval} days.' )
    graph3.write('{:.2%}'.format(avg_rus2k_return))

else:
    pass