import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
import math
from datetime import datetime
import sys
from functools import reduce
sys.path.append("..")

from functions.generate_db import *

st.set_page_config(layout="wide")

# -------- DATE SELECTION SECTION --------
    # --- DATE SELECTION ---
today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
header_col1, header_col2 = st.columns(2)
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
st.sidebar.subheader("Global Parameters used with WTDOLLE")
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
hyg_show = st.sidebar.checkbox("High Yield Junk Bonds - HYG", value=False)
if hyg_show == True:
    sidebar_counter += 1
st.sidebar.divider()

    # --- RSP OPTIONS ---
show_rsp = st.sidebar.checkbox("Overall S&P Market Thrust", value=False)
if show_rsp == True:
    rspMAorRSI = st.sidebar.multiselect(
        'Choose your RSP parameters',
        ['Moving Average (MA)', 'RSI (Relative Strength Index)']
    )
    st.sidebar.write("")
    if 'Moving Average (MA)' in rspMAorRSI:
        st.sidebar.subheader('RSP Moving Average')
        sidebar_counter += 1
        rsp_ma_length = int(st.sidebar.text_input("Input Moving Average Length (interval)", 50, key='rsp ma length'))
        rsp_comparator_selection = st.sidebar.radio('Choose RSP comparator',
                                                    ['Price greater than MA', "Price less than MA"],
                                                    index = 0)
        
        st.sidebar.write("")
    
    if 'RSI (Relative Strength Index)' in rspMAorRSI:
        st.sidebar.subheader('RSP RSI')
        sidebar_counter += 1
        rsp_rsi_length = int(st.sidebar.text_input('Input RSI length', 22, key = 'rsp rsi length'))
        rsp_rsi_comparator = st.sidebar.radio('Choose RSP RSI comparator',
                                            ['Greater than', 'Less than'],
                                            index=0,
                                            key = 'rsp rsi comparator')
        #TODO build query development in same place as selection to include value.
        rsp_rsi_value_selection = int(st.sidebar.text_input("Input RSI value to compare against",
                                              70,
                                              key='rsp rsi value selection'))


else:
    pass
st.sidebar.divider()

    # --- YIELD CURVE --- TODO Implement Yield Curve implementation
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
    yieldcurve_level = float(st.sidebar.text_input("Input Yield Difference to compare",
                                                 1.2,
                                                 key = 'Yield Curve level'))
    
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
sp500_intersection = []
nasdaq_intersection = []
rus2k_intersection = []

# ----- SELECTED VARIABLES COLUMNS ---------
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

# ---VIX---
with col1:
    if vix_show == True:
        vix_metric, vix_level, str_vix_pct_change, vix_pct_change_floor, vix_pct_change_ceil = generate_vix(start_date, input_end_date, interval_input)

        if vix_show_label == "VIX % Change":
            st.metric(label = "VIX % Change", value = str_vix_pct_change)

            #Generate filtered dataset with selected parameters
            filtered_vix_metric = vix_metric[(vix_metric['% Change'] >= vix_pct_change_floor) & (vix_metric['% Change'] <= vix_pct_change_ceil)]
            sp500_intersection.append(filtered_vix_metric)
            nasdaq_intersection.append(filtered_vix_metric)
            rus2k_intersection.append(filtered_vix_metric)
        else:
            if vix_comparator_selection == 'Greater than:':
                vix_boolean = vix_level >= vix_comparator_value
                st.metric(label=f'VIX > {vix_comparator_value}', value = f'{vix_boolean} @ {"{:.0f}".format(vix_level)}')
                filtered_vix_metric = vix_metric[vix_metric['Close'] >= vix_comparator_value]
                sp500_intersection.append(filtered_vix_metric)
                nasdaq_intersection.append(filtered_vix_metric)
                rus2k_intersection.append(filtered_vix_metric)

            else:
                vix_boolean = vix_level <= vix_comparator_value
                st.metric(label=f'VIX < {vix_comparator_value}', value = f'{vix_boolean} @ {"{:.0f}".format(vix_level)}')
                filtered_vix_metric = vix_metric[vix_metric['Close'] <= vix_comparator_value]
                sp500_intersection.append(filtered_vix_metric)
                nasdaq_intersection.append(filtered_vix_metric)
                rus2k_intersection.append(filtered_vix_metric)

# ---HYG---
with col2:
     if hyg_show == True:
        hyg_metric, str_hyg_pct_change, int_hyg_pct_change, hyg_pct_change_floor, hyg_pct_change_ceil = generate_hyg(start_date, input_end_date, interval_input)

        #Generate filtered dataset with selected parameters
        filtered_hyg_metric = hyg_metric[(hyg_metric['% Change'] >= hyg_pct_change_floor) & (hyg_metric['% Change'] <= hyg_pct_change_ceil)]
        sp500_intersection.append(filtered_hyg_metric)
        nasdaq_intersection.append(filtered_hyg_metric)
        rus2k_intersection.append(filtered_hyg_metric)

        #Show metric
        st.metric(label = "HYG % Change", value = str_hyg_pct_change)

#---RSP---
if show_rsp == True:
    if 'Moving Average (MA)' in rspMAorRSI and 'RSI (Relative Strength Index)' in rspMAorRSI:
        rsp_metric, rsp_price, rsp_ma, rsp_rsi_level = generate_rsp(start_date, input_end_date, interval_input, ma_length = rsp_ma_length, rsi_value = rsp_rsi_length)
    elif 'Moving Average (MA)' in rspMAorRSI:
        rsp_metric, rsp_price, rsp_ma, rsp_rsi_level = generate_rsp(start_date, input_end_date, interval_input, ma_length = rsp_ma_length)
    elif 'RSI (Relative Strength Index)' in rspMAorRSI:
        rsp_metric, rsp_price, rsp_ma, rsp_rsi_level = generate_rsp(start_date, input_end_date, interval_input, rsi_value = rsp_rsi_length)

    with col3:
        if 'Moving Average (MA)' in rspMAorRSI:
            if rsp_comparator_selection == 'Price greater than MA':
                rsp_boolean = rsp_price > rsp_ma
                st.metric(label=f'Price > ({rsp_ma_length}) MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_boolean} @ {"{:.0f}".format(rsp_price)}')
                filtered_rsp_ma_metric = rsp_metric[rsp_metric['Close'] > rsp_metric['ma']]
                sp500_intersection.append(filtered_rsp_ma_metric)
                nasdaq_intersection.append(filtered_rsp_ma_metric)
                rus2k_intersection.append(filtered_rsp_ma_metric)

            else:
                rsp_boolean = rsp_price < rsp_ma
                st.metric(label=f'Price < ({rsp_ma_length}) MA {"{:.0f}".format(rsp_ma)}', value = f'{rsp_boolean} @ {"{:.0f}".format(rsp_price)}')
                filtered_rsp_ma_metric = rsp_metric[rsp_metric['Close'] < rsp_metric['ma']]
                sp500_intersection.append(filtered_rsp_ma_metric)
                nasdaq_intersection.append(filtered_rsp_ma_metric)
                rus2k_intersection.append(filtered_rsp_ma_metric)

    with col4:
        if 'RSI (Relative Strength Index)' in rspMAorRSI:
            if rsp_rsi_comparator == 'Greater than':
                rsp_rsi_boolean = rsp_rsi_level > rsp_rsi_value_selection
                st.metric(label=f'RSP ({rsp_rsi_length}) RSI > {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_level)}')
                filtered_rsp_rsi_metric = rsp_metric[rsp_metric['rsi'] > rsp_rsi_value_selection]
                sp500_intersection.append(filtered_rsp_rsi_metric)
                nasdaq_intersection.append(filtered_rsp_rsi_metric)
                rus2k_intersection.append(filtered_rsp_rsi_metric)

            else:
                rsp_rsi_boolean = rsp_rsi_level < rsp_rsi_value_selection
                st.metric(label=f'RSP ({rsp_rsi_length}) RSI < {rsp_rsi_value_selection}', value = f'{rsp_rsi_boolean} @ {"{:.0f}".format(rsp_rsi_level)}')
                filtered_rsp_rsi_metric = rsp_metric[rsp_metric['rsi'] < rsp_rsi_value_selection]
                sp500_intersection.append(filtered_rsp_rsi_metric)
                nasdaq_intersection.append(filtered_rsp_rsi_metric)
                rus2k_intersection.append(filtered_rsp_rsi_metric)

#---YIELD CURVE---
with col5:
    if show_yieldcurve == True:
        if show_yield_option == '30-year':
            yielddiff, curr_yielddiff, curr_ltyield, curr_styield = yield_difference(start_date,
                                            input_end_date,
                                            lt_yield_inp='30y')
            if yieldcurve_comparator_selection == "Diff greater than":
                yield_boolean = curr_yielddiff >= yieldcurve_level
                st.metric(label=f'Yield Diff > {yieldcurve_level}', value = f'{yield_boolean} @ {curr_yielddiff}')
                
                filtered_yielddiff_metric = yielddiff[yielddiff['Yield Difference'] >= yieldcurve_level]
                sp500_intersection.append(filtered_yielddiff_metric)
                nasdaq_intersection.append(filtered_yielddiff_metric)
                rus2k_intersection.append(filtered_yielddiff_metric)

            else:
                yield_boolean = curr_yielddiff <= yieldcurve_level
                st.metric(label=f'Yield Diff < {yieldcurve_level}', value = f'{yield_boolean} @ {curr_yielddiff}')

                filtered_yielddiff_metric = yielddiff[yielddiff['Yield Difference'] <= yieldcurve_level]
                sp500_intersection.append(filtered_yielddiff_metric)
                nasdaq_intersection.append(filtered_yielddiff_metric)
                rus2k_intersection.append(filtered_yielddiff_metric)


            st.line_chart(yielddiff['Yield Difference'], #TODO add chart to other variables
                          use_container_width = True,
                          height = 100)
        
        else:
            yielddiff, curr_yielddiff, curr_ltyield, curr_styield = yield_difference(start_date,
                                            input_end_date,
                                            lt_yield_inp='10y')
            if yieldcurve_comparator_selection == "Diff greater than":
                yield_boolean = curr_yielddiff >= yieldcurve_level
                st.metric(label=f'Yield Diff > {yieldcurve_level}', value = f'{yield_boolean} @ {curr_yielddiff}')

            else:
                yield_boolean = curr_yielddiff <= yieldcurve_level
                st.metric(label=f'Yield Diff < {yieldcurve_level}', value = f'{yield_boolean} @ {curr_yielddiff}')


            st.line_chart(yielddiff['Yield Difference'],
                          use_container_width = True,
                          height = 100)
    pass

st.write("")
st.write("")

        
#--- PLOTTING GRAPH ---
col1, col2, col3 = st.columns(3)
graph1, graph2, graph3= st.columns(3)

#-------INDICES PARAMETER SELECTION-------
col1.subheader("S&P 500")
with col1.expander("S&P500 Parameter Selection"):
    sp500col1, sp500col2 = st.columns(2)
    with sp500col1:
        sp500_return_interval = int(st.text_input("# of intervals to calculate return", 10, key="sp500 return interval"))
    with sp500col2:
        sp500rsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='sp500 RSI show')
        if sp500rsishow:
            sp500_rsi_length = int(st.text_input('Select RSI length (in intervals)', 22, key = "sp500 RSI length")) 
            sp500, sp500rsicurrent = generate_sp500(start_date, input_end_date, interval=interval_input, rsi_value=sp500_rsi_length)

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
            sp500, sp500rsicurrent = generate_sp500(start_date, input_end_date, interval=interval_input)

col2.subheader("Nasdaq")
with col2.expander("Nasdaq Parameter Section"):
    ndxcol1, ndxcol2 = st.columns(2)
    with ndxcol1:
        ndx_return_interval = int(st.text_input("# of intervals to calculate return", 10, key="ndx return interval"))
    with ndxcol2:
        ndxrsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='ndx RSI show')
        if ndxrsishow:
            ndx_rsi_length = int(st.text_input('Select RSI length (in intervals)', 22, key = "ndx RSI length"))
            ndx, ndxrsicurrent = generate_ndx(start_date, input_end_date, interval=interval_input, rsi_value=ndx_rsi_length)
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
            ndx, ndxrsicurrent = generate_ndx(start_date, input_end_date, interval=interval_input)

col3.subheader("Russell 2000")
with col3.expander("Russell 2000 Parameter Section"):
    rus2kcol1, rus2kcol2 = st.columns(2)
    with rus2kcol1:
        rus2k_return_interval = int(st.text_input("# of intervals to calculate return", 10, key="rus2k return interval"))
    with rus2kcol2:
        rus2krsishow = st.checkbox("Overbought/Oversold RSI Indicator", value=False, key='rus2k RSI show')
        if rus2krsishow:
            rus2k_rsi_length = int(st.text_input('Select RSI lenght (in intervals)', 22, key = "rus2k RSI length"))
            rus2k, rus2krsicurrent = generate_rus2k(start_date, input_end_date, interval=interval_input, rsi_value=rus2k_rsi_length)
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
            rus2k, rus2krsicurrent = generate_rus2k(start_date, input_end_date, interval=interval_input)

#---S&P500 REPORTING---
sp500_index_columns = [df.index for df in sp500_intersection]
sp500_common_index = reduce(lambda left, right: left.intersection(right), sp500_index_columns).to_list()

sp500['% Change Sel Interval'] = sp500['Close'].pct_change(sp500_return_interval).shift(-sp500_return_interval)
sp500_common = sp500[sp500.index.isin(sp500_common_index)]

    #-------S&P500 GRAPH------
fig, ax = plt.subplots()
ax.set_title('S&P500')
ax.plot(sp500.index, sp500['Close'], linewidth = 0.5, color='black')
ax.scatter(sp500_common.index, sp500_common['Close'], marker='.', color='red', s = 10)
graph1.pyplot(fig)

    #-------S&P500 GENERATE STATEMENTS--------
average_sp500_return = sp500_common['% Change Sel Interval'].mean()
sp500_number_of_occurrences = len(sp500_common['% Change Sel Interval'])
sp500_number_of_positives = (sp500_common['% Change Sel Interval'] > 0).sum()
sp500_positive_percentage = sp500_number_of_positives/sp500_number_of_occurrences
sp500_positive_percentage = '{:.2%}'.format(sp500_positive_percentage)

graph1.write(f'This occurred {sp500_number_of_occurrences} of time(s) and is {sp500_positive_percentage} positive in {sp500_return_interval} days.' )
graph1.write('{:.2%}'.format(average_sp500_return))

#--_NASDAQ REPORTING
ndx_index_columns = [df.index for df in nasdaq_intersection]
ndx_common_index = reduce(lambda left, right: left.intersection(right), ndx_index_columns).to_list()

ndx["% Change Sel Interval"] = ndx['Close'].pct_change(ndx_return_interval).shift(-ndx_return_interval)
ndx_common = ndx[ndx.index.isin(ndx_common_index)]

    #-------NASDAQ GRAPH------
fig, ax = plt.subplots()
ax.set_title('Nasdaq 100')
ax.plot(ndx.index, ndx['Close'], linewidth = 0.5, color='black')
ax.scatter(ndx_common.index, ndx_common['Close'], marker='.', color='red', s = 10)
graph2.pyplot(fig)

    #-------NASDAQ GENERATE STATEMENTS-------
average_ndx_return = ndx_common['% Change Sel Interval'].mean()
ndx_number_of_occurrences = len(ndx_common['% Change Sel Interval'])
ndx_number_of_positives = (ndx_common['% Change Sel Interval'] > 0).sum()
ndx_positive_percentage = ndx_number_of_positives/ndx_number_of_occurrences
ndx_positive_percentage = '{:.2%}'.format(ndx_positive_percentage)

graph2.write(f'This occurred {ndx_number_of_occurrences} time(s) and is {ndx_positive_percentage} positive in {ndx_return_interval} days.' )
graph2.write('{:.2%}'.format(average_ndx_return))

#--RUSSEL 2000 REPORTING
rus2k_index_columns = [df.index for df in rus2k_intersection]
rus2k_common_index = reduce(lambda left, right: left.intersection(right), rus2k_index_columns).to_list()

rus2k["% Change Sel Interval"] = rus2k['Close'].pct_change(rus2k_return_interval).shift(-rus2k_return_interval)
rus2k_common = rus2k[rus2k.index.isin(rus2k_common_index)]

#-----RUSSELL 2000 GRAPH-----
fig, ax = plt.subplots()
ax.set_title('Russel 2000')
ax.plot(rus2k.index, rus2k['Close'], linewidth = 0.5, color='black')
ax.scatter(rus2k_common.index, rus2k_common['Close'], marker='.', color='red', s = 10)
graph3.pyplot(fig)

    #-------NASDAQ GENERATE STATEMENTS-------
average_rus2k_return = rus2k_common['% Change Sel Interval'].mean()
rus2k_number_of_occurrences = len(rus2k_common['% Change Sel Interval'])
rus2k_number_of_positives = (rus2k_common['% Change Sel Interval'] > 0).sum()
rus2k_positive_percentage = rus2k_number_of_positives/rus2k_number_of_occurrences
rus2k_positive_percentage = '{:.2%}'.format(rus2k_positive_percentage)

graph3.write(f'This occurred {rus2k_number_of_occurrences} of time(s) and is {rus2k_positive_percentage} positive in {rus2k_return_interval} days.' )
graph3.write('{:.2%}'.format(average_rus2k_return))