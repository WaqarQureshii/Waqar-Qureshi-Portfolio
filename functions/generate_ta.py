#%%
import pandas_ta as ta

import generate_db

#%%
def sp500_rsi(start_date,
              rsi_lt = 30,
              rsi_mt = 15,
              rsi_st = 5):
    sp500 = generate_db.generate_sp500(start_date)
    sp500[f'rsi{rsi_lt}'] = ta.rsi(close = sp500.Close, length=rsi_lt)
    sp500[f'rsi{rsi_mt}'] = ta.rsi(close = sp500.Close, length=rsi_mt)
    sp500[f'rsi{rsi_st}'] = ta.rsi(close = sp500.Close, length=rsi_st)
    return sp500

def sp500_bbands(start_date,
                 bbands_length = 20,
                 bbands_std = 2):
    
    my_bbands = ta.bbands(close = sp500_ta.Close, length=bbands_length, std=bbands_std)
    sp500_ta=sp500_ta.join(my_bbands)
    