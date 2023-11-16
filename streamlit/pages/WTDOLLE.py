import streamlit as st
import pandas as pd
from datetime import datetime

import sys
sys.path.append("..")

from functions.generate_db import generate_vix


show_vix = st.checkbox('VIX')

if show_vix == True:
    show_vix_label = st.radio('Choose Signal Type',
                              ["VIX level", 'VIX % Change'])
else:
    pass

show_hyg = st.checkbox('HYG')
if show_hyg == True:
    show_hyg_label = st.radio('Choose Signal Type',
                              ["HYG level", 'HYG % Change'])
else:
    pass