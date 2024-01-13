import streamlit as st
import pandas as pd
import pandas_ta as ta

from functools import reduce
from datetime import datetime

import sys
sys.path.append("..")
from functions.generate_db import *

today_date = datetime.today()
start_date = '2001-01-01 00:00:00'
start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

header_col1, header_col2 = st.columns(2)
start_date = header_col1.date_input(label = "Choose start date", value = start_date)
input_end_date = header_col1.date_input(label = 'Choose end date', value = today_date)

sp500, sp500rsicurrent = generate_sp500(start_date=start_date, end_date=input_end_date, interval="1d") #TODO add input for interval selection

sp500['% Change'] = pd.to_numeric(sp500['% Change'], errors='coerce')
sp500['Total Positives'] = (sp500['% Change'] > 0).cumsum()

# Count the rows without resetting the index
row_count = sp500.shape[0]

# Add a new column 'Row Number'
sp500['Row Number'] = range(1, row_count + 1)

sp500['% Positive'] = sp500['Total Positives']/sp500['Row Number']
sp500['ma'] = ta.sma(close = sp500['% Positive'], length = 30)
# st.dataframe(sp500)   

st.line_chart(sp500, y = ['ma', '% Positive'])