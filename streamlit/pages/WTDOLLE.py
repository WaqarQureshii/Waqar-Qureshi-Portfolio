# import streamlit as st
import pandas as pd
from datetime import datetime

from functions.generate_db import *
from functions.last_business_date import *

interval_options = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

interval = '1wk'
start_date = '2008-01-01'

vix = generate_vix(start_date, interval = interval)
print(vix)


# today = today_date()

# st.subheader("VIX")
# print(today)

