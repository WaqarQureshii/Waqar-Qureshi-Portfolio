import streamlit as st
import pandas as pd
from datetime import datetime

import sys
sys.path.append("..")

from functions.generate_db import generate_vix


col1, col2, col3, col4, col5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])

with col1:
    st.write("Volatility Index")
    
    show_vix = st.checkbox('VIX')
    if show_vix == True:
        show_vix_label = st.radio('Choose Signal Type',
                                ["VIX level", 'VIX % Change'])
    else:
        pass


with col2:
    st.write("Junk Bonds")
    show_hyg = st.checkbox('HYG')
    if show_hyg == True:
        show_hyg_label = st.radio('Choose Signal Type',
                                ["HYG level", 'HYG % Change'])
    else:
        pass

with col3:
    st.write("Overbought / Oversold")
    show_RSI = st.checkbox("RSI")
    if show_hyg == True:
        show_hyg_label = st.text_input("RSI metric", "<20")
    else:
        pass

with col4:
    st.write("Market Thrust")
    show_rsp = st.checkbox("RSP")

with col5:
    st.write("Yield Curve")
    show_yield = st.checkbox("Yield Curve")
    if show_yield == True:
        show_hyg_label = st.radio('3-month vs ',
                                  ["10-year", "30-year"])
    else:
        pass