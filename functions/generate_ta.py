import pandas_ta as ta
import pandas as pd

import generate_db

def sp500_rsi(start_date,
              rsi_lt = 30,
              rsi_mt = 15,
              rsi_st = 5):
    sp500 = generate_db.generate_sp500(start_date)
    sp500[f'rsi_{rsi_lt}'] = ta.rsi(close = sp500.Close, length=rsi_lt)
    sp500[f'rsi_{rsi_mt}'] = ta.rsi(close = sp500.Close, length=rsi_mt)
    sp500[f'rsi_{rsi_st}'] = ta.rsi(close = sp500.Close, length=rsi_st)
    return sp500

def sp500_bbands(start_date,
                 bbands_length = 20,
                 bbands_std = 2):
    sp500 = generate_db.generate_sp500(start_date)
    my_bbands = ta.bbands(close = sp500.Close, length=bbands_length, std=bbands_std)
    # maybe look into renaming bbands if necessary
    sp500 = sp500.join(my_bbands)
    return sp500

def yield_difference(start_date, lt_yield_inp = '30y'):
    if lt_yield_inp == '30y':
        lt_yield = generate_db.generate_30yrx(start_date)
    else:
        lt_yield = generate_db.generate_10yrx(start_date)
    
    st_yield = generate_db.generate_3mrx(start_date)
    
    yield_diff = pd.concat([lt_yield, st_yield], axis=1)
    yield_diff['yield_diff'] = lt_yield - st_yield
    return yield_diff
