import pandas_ta as ta
import pandas as pd

import generate_db

def nasdaqvssp500(start_date, interval = '1d'):
    nasdaq = generate_db.generate_ndx(start_date, interval=interval)
    nasdaq.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    nasdaq.rename(columns)

    sp500 = generate_db.generate_sp500(start_date, interval=interval)
    # sp500.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    
    # ndxvssp500 = pd.concat([nasdaq, sp500], axis=1)
    # ndxvssp500['Nasdaq vs SP500 Ratio'] = ndxvssp500['Nasdaq Close']/ndxvssp500['SP500 Close']
    # ndxvssp500.drop(['Nasdaq Close', 'SP500 Close', 'SP500 % Change'], axis = 1, inplace=True)
    
    return nasdaq

def sp500_rsi(start_date,
              rsi_lt = 30,
              rsi_mt = 15,
              rsi_st = 5,
              interval = '1d'):
    sp500 = generate_db.generate_sp500(start_date, interval = interval)
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
    #LONG-TERM YIELD GENERATION
    if lt_yield_inp == '30y':
        lt_yield = generate_db.generate_30yrx(start_date)
    else:
        lt_yield = generate_db.generate_10yrx(start_date)
    lt_yield.rename(columns={'Close': 'Long Term Yield'}, inplace=True)
    #SHORT TERM YIELD GENERATION
    
    st_yield = generate_db.generate_3mrx(start_date)
    st_yield.rename(columns={'Close': 'Short Term Yield'}, inplace=True)

    #CALCULATING YIELD DIFFERENCE
    dt_yield_diff = pd.concat([lt_yield, st_yield], axis = 1)
    dt_yield_diff['Yield Difference'] = dt_yield_diff['Long Term Yield'] - dt_yield_diff['Short Term Yield']
    return dt_yield_diff

test = nasdaqvssp500('2023-01-01')
print(test)
    
    