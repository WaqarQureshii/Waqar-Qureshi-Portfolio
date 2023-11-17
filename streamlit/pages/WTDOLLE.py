import streamlit as st
import pandas as pd
from datetime import datetime

import sys
sys.path.append("..")

from functions.generate_db import generate_vix

st.set_page_config(layout="wider")
st.write('''
# WTDOLLE
## This is what happened today with these variables:
''')

with st.expander("Variables to include/exclude (select):"):
    col1, col2, col3, col4, col5, col6, col7, col8= st.columns(8)
    with col1:
        st.write("Volatility Index")
        
        show_vix = st.checkbox('VIX', value=True)
        if show_vix == True:
            show_vix_label = st.radio('Choose Signal Type',
                                    ['VIX % Change' ,"VIX level"],
                                    index=0)
        else:
            pass

    with col2:
        st.write("Junk Bonds")
        show_hyg = st.checkbox('HYG', value=True)
        
    with col3:
        st.write("Overbought / Oversold")
        show_rsi = st.checkbox("RSI", value=True)
        if show_rsi == True:
            show_rsi_label = st.text_input("RSI metric", "<20")
        else:
            pass

    with col4:
        st.write("Market Thrust")
        show_rsp = st.checkbox("RSP")

    with col5:
        st.write("Yield Curve")
        show_yield = st.checkbox("Yield Curve", value=True)
        if show_yield == True:
            show_yield_label = st.radio('3-month vs ',
                                    ["10-year", "30-year"],
                                    index=1)

            show_yield_metric = st.radio('Choose Yield Metric:',
                                         ['Yield Curve % Change',
                                          'Yield Curve Value'])
        else:
            pass

    with col6:
        st.write("Consumer")
        show_consumer = st.checkbox("XLY")

    with col7:
        st.write("Utility")
        show_consumer = st.checkbox("XLU")

    with col8:
        st.write("Nasdaq vs SP500 Ratio")
        show_ndxVSsp = st.checkbox("NDX vs SP500")
        if show_ndxVSsp == True:
            show_ndxVSsp_label = st.radio('NDX vs SP500',
                                          ['% Change',
                                           'Ratio'])