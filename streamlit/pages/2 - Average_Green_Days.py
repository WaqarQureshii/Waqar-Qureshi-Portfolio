import streamlit as st
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

from functools import reduce
from datetime import datetime

import sys
sys.path.append("..")
from functions.generate_db import *
from functions.average_green_days import *

today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
moving_average_length = 60
interval_selection = '1d'

header_col1, header_col2 = st.columns(2)
start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

graph1, graph2 = st.columns(2)

sp500 = percent_positive(start_date, input_end_date, interval_selection, moving_average_length)

graph1.line_chart(sp500, y = ['ma', '% Positive'])


fig, ax = plt.subplots()
ax.plot(sp500.index, sp500['% Positive'], linewidth = 0.5, color='black')
graph2.pyplot(fig)