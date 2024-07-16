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
header_col1, header_col2 = st.columns(2)
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
    vix = Generate_DB()
    vix.get_database('^VIX', input_start_date, input_end_date, input_interval)

    selected_signal_vix = st.sidebar.radio('Choose Signal Type',
                            [f'VIX % Change: {vix.pctchg_str}' ,f'VIX level: {round(vix.curr_p,1)}'],
                            index=0)

    if selected_signal_vix == f'VIX level: {round(vix.curr_p,1)}':
# ------ VIX UI for VIX level selection ------
        subheader_comparator_vix = st.sidebar.radio('Choose VIX comparator',
                                                    ['Greater than', "Less than"],
                                                    index = 1,
                                                    key = "comparator vix level selector")
        selected_value_vix = int(st.sidebar.text_input("Input VIX integer (##)", value = int(vix.curr_p+1))) #TODO add intelligent default values

        if subheader_comparator_vix == 'Greater than':
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_selection('current price', subheader_comparator_vix, selected_value_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col1.metric(label=f'VIX > {selected_value_vix}', value = f'{vix.boolean_comp} @ {"{:.0f}".format(vix.curr_p)}')

        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_selection('current price', subheader_comparator_vix, selected_value_vix, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col1.metric(label=f'VIX < {selected_value_vix}', value = f'{vix.boolean_comp} @ {"{:.0f}".format(vix.curr_p)}')
        
        col1.line_chart(vix.db['Close'], height = 100, use_container_width = True)

# ------ VIX UI for VIX % Change Selection ------
    else:
        subheader_comparator_vix = st.sidebar.radio('Choose VIX comparator',
        ['Greater than', "Less than"],
        index = 1, key = "comparator vix pct selector")
        selected_pct_change = float(st.sidebar.text_input("Input percent increase/decrease", value = 
        vix.pctchg_ceil_int*100, key = 'VIX pct comparator value'))
        
        if subheader_comparator_vix == 'Greater than':
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_selection('% change', subheader_comparator_vix, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col1.metric(label = f"VIX % > {selected_pct_change}", value = f'{vix.boolean_comp} @ {vix.pctchg_str}')
        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = vix.metric_vs_selection('% change', subheader_comparator_vix, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col1.metric(label = f"VIX % < {selected_pct_change}", value = f'{vix.boolean_comp} @ {vix.pctchg_str}')
        
        col1.line_chart(vix.db['% Change']*100, height = 100, use_container_width = True)
else:
    pass
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
        sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_selection('% change', subheader_comparator_hyg, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        
        col2.metric(label = f"HYG % > {selected_pct_change}", value = f'{hyg.boolean_comp} @ {hyg.pctchg_str}')
    else:
        sp500_intersection, nasdaq_intersection, rus2k_intersection = hyg.metric_vs_selection('% change', subheader_comparator_hyg, selected_pct_change, sp500_intersection, nasdaq_intersection, rus2k_intersection)
        
        col2.metric(label = f"HYG % < {selected_pct_change}", value = f'{hyg.boolean_comp} @ {hyg.pctchg_str}')
    
    col2.line_chart(hyg.db['% Change']*100, height = 100, use_container_width = True)

st.sidebar.divider()

    # --- RSP OPTIONS ---
header_show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if header_show_rsp == True:
    rspMAorRSI = st.sidebar.multiselect('Choose your RSP parameters', ['Moving Average (MA)', 'RSI (Relative Strength Index)'])
    st.sidebar.write("")

# BOTH Price vs MA and RSI selected
    if 'Moving Average (MA)' in rspMAorRSI and 'RSI (Relative Strength Index)' in rspMAorRSI:
        st.sidebar.subheader('RSP Moving Average') #---MOVING AVERAGE SECTION---

        sidebar_counter += 2
        rsp_ma_length = int(st.sidebar.text_input(f"Input Moving Average Length (in {grammatical_selection})", 50, key='rsp ma length'))
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
        rsp = Generate_DB()
        rsp.get_database('RSP', input_start_date, input_end_date, input_interval, ma_length=rsp_ma_length, rsi_value=rsp_rsi_length)
# ONLY Price vs MA selected
        if rsp_macomparator_selection == "Price greater than MA": #---Moving Average Signal generator---
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('price vs ma', 'Greater than', selected_value=None, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection) #TODO need to change the metric to be "whenever price crosses MA", and not "every single time Price is over"
            
            col3.metric(label=f'Price > {rsp_ma_length} {grammatical_selection} MA {"{:.0f}".format(rsp.curr_ma)}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_p)}')

        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('price vs ma', 'Less than', selected_value=None, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            col3.metric(label=f'Price < {rsp_ma_length} {grammatical_selection} MA {"{:.0f}".format(rsp.curr_ma)}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_p)}')

# ONLY RSI selected
        if rsp_rsi_comparator == 'Greater than': #---RSI Signal generator---
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('rsi vs selection', rsp_rsi_comparator, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col4.metric(label=f'RSP {rsp_rsi_length} {grammatical_selection} RSI > {rsp_rsi_value_selection}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_rsi)}')
        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('rsi vs selection', rsp_rsi_comparator, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col4.metric(label=f'RSP {rsp_rsi_length} {grammatical_selection} RSI < {rsp_rsi_value_selection}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_rsi)}')
        
        col3.line_chart(rsp.db['ma'], height = 100, use_container_width = True)
        col4.line_chart(rsp.db['rsi'], height = 100, use_container_width = True)

    elif 'Moving Average (MA)' in rspMAorRSI:
        st.sidebar.subheader('RSP Moving Average')

        sidebar_counter += 1
        rsp_ma_length = int(st.sidebar.text_input("Input Moving Average Length (interval)", 50, key='rsp ma length'))

        rsp = Generate_DB()
        rsp.get_database('RSP', input_start_date, input_end_date, input_interval, ma_length=rsp_ma_length)

        rsp_comparator_selection = st.sidebar.radio('Choose RSP comparator',
                                                    ['Price greater than MA', "Price less than MA"],
                                                    index = 0)
        
        if rsp_comparator_selection == "Price greater than MA":
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('price vs ma', 'Greater than', selected_value=None, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            col3.metric(label=f'Price > {rsp_ma_length} {grammatical_selection} MA {"{:.0f}".format(rsp.curr_ma)}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_p)}')

        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('price vs ma', 'Lower than', selected_value=None, sp500=sp500_intersection, ndx=nasdaq_intersection, rus2k=rus2k_intersection)

            col3.metric(label=f'Price < {rsp_ma_length} {grammatical_selection} MA {"{:.0f}".format(rsp.curr_ma)}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_p)}')

        col3.line_chart(rsp.db['ma'], height = 100, use_container_width = True)

        st.sidebar.write("")
    
    elif 'RSI (Relative Strength Index)' in rspMAorRSI:
        st.sidebar.subheader('RSP RSI')
        rsp_rsi_length = int(st.sidebar.text_input('Input RSI length', 22, key = 'rsp rsi length'))

        sidebar_counter += 1
        rsp = Generate_DB()
        rsp.get_database('RSP', input_start_date, input_end_date, input_interval, rsi_value=rsp_rsi_length)
        
        rsp_rsi_comparator = st.sidebar.radio('Choose RSP RSI comparator',
                                            ['Greater than', 'Less than'],
                                            index=0,
                                            key = 'rsp rsi comparator')

        rsp_rsi_value_selection = int(st.sidebar.text_input("Input RSI value to compare against",
                                              70,
                                              key='rsp rsi value selection'))
        
        if rsp_rsi_comparator == 'Greater than': #---RSI Signal generator---
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('rsi vs selection', rsp_rsi_comparator, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            
            col4.metric(label=f'RSP ({rsp_rsi_length}) RSI > {rsp_rsi_value_selection}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_rsi)}')
        else:
            sp500_intersection, nasdaq_intersection, rus2k_intersection = rsp.metric_vs_selection('rsi vs selection', rsp_rsi_comparator, rsp_rsi_value_selection, sp500_intersection, nasdaq_intersection, rus2k_intersection)

            col4.metric(label=f'RSP ({rsp_rsi_length}) RSI < {rsp_rsi_value_selection}', value = f'{rsp.boolean_comp} @ {"{:.0f}".format(rsp.curr_rsi)}')   
        
        col4.line_chart(rsp.db['rsi'], height = 100, use_container_width = True)

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
        yielddiff = Generate_Yield(input_start_date, input_end_date, input_interval).calc_yield_diff('^IRX', '^TYX')
        
        if yieldcurve_comparator_selection == "Diff greater than": # Current Yield Curve greater than Selected Difference Value
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_greater(yielddiff.yield_diff, yielddiff.curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff > {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {yielddiff.curr_yielddiff}')
        
        else: # Current Yield Curve less than Selected Difference Value
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_lower(yielddiff.yield_diff, yielddiff.curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff < {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {yielddiff.curr_yielddiff}')
    
    else:
        yielddiff = Generate_Yield(input_start_date, input_end_date, input_interval).calc_yield_diff('^IRX', '^TNX')
        
        if yieldcurve_comparator_selection == "Diff greater than":
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_greater(yielddiff.yield_diff, yielddiff.curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff > {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {yielddiff.curr_yielddiff}')

        else:
            yield_boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection = yieldcurve_diff_lower(yielddiff.yield_diff, yielddiff.curr_yielddiff, selected_yieldcurve_diff, sp500_intersection, nasdaq_intersection, rus2k_intersection)
            col5.metric(label=f'Yield Diff < {selected_yieldcurve_diff}', value = f'{yield_boolean} @ {yielddiff.curr_yielddiff}')


    col5.line_chart(yielddiff.yield_diff['Yield Diff'],
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
        
        db_ndxsp500, current_ratio_ndxsp500, current_ratio_pct_ndxsp500, current_ratio_pct_ndxsp500_str, nasdaq, sp500 = nasdaqvssp500(input_start_date, input_end_date, input_interval)

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

        db_ndxsp500, curr_ndxsp500_ratio, current_ratio_pct_ndxsp500, current_ratio_pct_ndxsp500_str, nasdaq, sp500 = nasdaqvssp500(input_start_date, input_end_date, input_interval)

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
        
        db_rus2ksp500, current_ratio_rus2ksp500, current_ratio_pct_rus2ksp500, current_ratio_pct_str_rus2ksp500, rus2k, sp500 = rus2kvssp500(input_start_date, input_end_date, input_interval)

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

        db_rus2ksp500, current_ratio_rus2ksp500, current_ratio_pct_rus2ksp500, current_ratio_pct_str_rus2ksp500, rus2k, sp500 = rus2kvssp500(input_start_date, input_end_date, input_interval)

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