import sys
sys.path.append("..")
from functions.generate_db import *

def percent_positive(start_date_selected, end_date_selected, interval_selected, ma_length_selected):
    sp500, sp500rsicurrent = generate_sp500(start_date=start_date_selected, end_date=end_date_selected, interval=interval_selected) #TODO add input for interval selection
    
    sp500['% Change'] = pd.to_numeric(sp500['% Change'], errors='coerce')
    sp500['Total Positives'] = (sp500['% Change'] > 0).cumsum()

    row_count = sp500.shape[0]

    sp500['Row Number'] = range(1, row_count + 1)
    last_index = sp500['Row Number'].iloc[-1]

    sp500['% Positive'] = sp500['Total Positives']/sp500['Row Number']
    sp500['ma'] = ta.sma(close = sp500['% Positive'], length = ma_length_selected)

    sp500 = sp500.tail(int(last_index*0.825))

    return sp500