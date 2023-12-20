import yfinance as yf
import pandas_ta as ta
import pandas as pd
import streamlit as st

import math

#--- GENERATING SP500 TABLE WITH % CHANGE AND RSI
@st.cache_data
def generate_sp500(start_date,
                   end_date,
                   interval = "1d",
                   rsi_value = 22):
    sp500 = yf.download(['^GSPC'],
                        start_date,
                        end_date,
                        interval)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    sp500['% Change'] = sp500['Close'].pct_change()
    sp500['rsi'] = ta.rsi(close = sp500.Close,
                          length=rsi_value)
    
    sp500rsicurrent = sp500['rsi'].iloc[-1]
    sp500rsicurrent = int(sp500rsicurrent)
    
    return sp500, sp500rsicurrent

#--- GENERATING RSP TABLE WITH % CHANGE, MA & RSI
@st.cache_data
def generate_rsp(start_date,
                 end_date,
                 interval = "1d",
                 ma_length = 50,
                 rsi_value = 22):
    rsp = yf.download(['RSP'],
                      start_date,
                      end_date,
                      interval)
    rsp = rsp.drop(["Adj Close", "High", "Low", "Volume", "Dividends", "Stock Splits", "Capital Gains"], axis=1)
    rsp['ma'] = ta.sma(close = rsp.Close, length = ma_length)
    rsp['% Change'] = rsp['Close'].pct_change()
    rsp['rsi'] = ta.rsi(close = rsp.Close,
                        length=rsi_value)
    
    rsp_price = rsp["Close"].iloc[-1]
    rsp_ma = rsp['ma'].iloc[-1]
    rsp_rsi_level = rsp['rsi'].iloc[-1]

    return rsp, rsp_price, rsp_ma, rsp_rsi_level

#--- GENERATING NASDAQ TABLE WITH % CHANGE, RSI
@st.cache_data
def generate_ndx(start_date,
                 end_date,
                 interval = '1d',
                 rsi_value = 22):
    ndx = yf.download(['^IXIC'],
                      start_date,
                      end_date,
                      interval)
    ndx = ndx.drop(["Adj Close"], axis=1)
    ndx['% Change'] = ndx['Close'].pct_change()
    ndx['rsi'] = ta.rsi(close = ndx.Close,
                        length = rsi_value)
    
    ndxrsicurrent = ndx['rsi'].iloc[-1]
    ndxrsicurrent = int(ndxrsicurrent)

    return ndx, ndxrsicurrent

#TODO do a calculation of average S&P daily return to assess if there is a pattern

#--- GENERATING RUSSEL 2000 TABLE WITH % CHANGE, RSI
@st.cache_data
def generate_rus2k(start_date,
                   end_date,
                   interval = '1d',
                   rsi_value = 22):
    rus2k = yf.download(['^RUT'],
                      start_date,
                      end_date,
                      interval)
    rus2k = rus2k.drop(["Adj Close"], axis=1)
    rus2k['% Change'] = rus2k['Close'].pct_change()
    rus2k['rsi'] = ta.rsi(close = rus2k.Close,
                            length = rsi_value)
    
    rus2krsicurrent = rus2k['rsi'].iloc[-1]
    rus2krsicurrent = int(rus2krsicurrent)

    return rus2k, rus2krsicurrent

@st.cache_data
def generate_vix(start_date, end_date, interval = '1d'):
    vix = yf.download(['^VIX'],
                      start_date,
                      end_date,
                      interval)
    vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)

    vix['% Change'] = vix['Close'].pct_change()

    vix_level = vix["Close"].iloc[-1]
    str_vix_pct_change = "{:.2%}".format(vix["% Change"].iloc[-1])
    int_vix_pct_change = vix["% Change"].iloc[-1]
    vix_pct_change_floor = math.floor(int_vix_pct_change*100)/100
    vix_pct_change_ceil = math.ceil(int_vix_pct_change*100)/100
    
    return vix, vix_level, str_vix_pct_change, vix_pct_change_floor, vix_pct_change_ceil

@st.cache_data
def generate_hyg(start_date, end_date, interval = '1d'):
    hyg = yf.download(['HYG'],
                      start_date,
                      end_date,
                      interval)
    
    hyg['% Change'] = hyg['Close'].pct_change()

    str_hyg_pct_change = "{:.2%}".format(hyg["% Change"].iloc[-1])
    int_hyg_pct_change = hyg["% Change"].iloc[-1]
    hyg_pct_change_floor = math.floor(int_hyg_pct_change*100)/100
    hyg_pct_change_ceil = math.ceil(int_hyg_pct_change*100)/100
    
    return hyg, str_hyg_pct_change, int_hyg_pct_change, hyg_pct_change_floor, hyg_pct_change_ceil


def generate_energy(start_date, end_date, interval = '1d'):
    energy = yf.download(['XLE'],
                         start_date,
                         end_date,
                         interval)
    
    energy['% Change'] = energy['Close'].pct_change()
    
    return energy


def generate_utility(start_date, end_date, interval = '1d'):
    utility = yf.download(['XLU'],
                          start_date,
                          end_date,
                          interval)
    
    utility['% Change'] = utility['Close'].pct_change()
    
    return utility


def generate_consumer(start_date, end_date, interval = '1d'):
    consumer = yf.download(['XLY'],
                           start_date,
                           end_date,
                           interval)
    
    consumer['% Change'] = consumer['Close'].pct_change()
    
    return consumer

def nasdaqvssp500(start_date, interval = '1d'):
    nasdaq = generate_ndx(start_date, interval)
    nasdaq.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    nasdaq.rename(columns={'Close':'Nasdaq Close'}, inplace=True)

    sp500 = generate_sp500(start_date, interval)
    sp500.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    sp500.rename(columns={'Close':'SP500 Close'}, inplace=True)

    ndxvssp500 = pd.concat([nasdaq, sp500], axis=1)
    ndxvssp500['Nasdaq vs SP500 Ratio'] = ndxvssp500['Nasdaq Close']/ndxvssp500['SP500 Close']
    ndxvssp500.drop(['Nasdaq Close', 'SP500 Close'], axis = 1, inplace=True)
    
    return ndxvssp500

def rus2kvssp500(start_date, end_date, interval = '1d'):
    rus2k = generate_rus2k(start_date, end_date, interval)
    rus2k.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    rus2k.rename(columns={'Close':'Russell 2000 Close'}, inplace=True)

    sp500 = generate_sp500(start_date, end_date, interval)
    sp500.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    sp500.rename(columns={'Close':'SP500 Close'}, inplace=True)

    rus2kvssp500 = pd.concat([rus2k, sp500], axis=1)
    rus2kvssp500['Russell 2000 vs SP500 Ratio'] = rus2kvssp500['Russell 2000 Close']/rus2kvssp500['SP500 Close']
    rus2kvssp500.drop(['Nasdaq Close', 'SP500 Close'], axis = 1, inplace=True)
    
    return rus2kvssp500

def sp500_ma(start_date,
             end_date,
             ma_length = 50,
             interval = '1d'):
    sp500 = generate_sp500(start_date, end_date, interval)
    sp500['ma'] = ta.sma(close = sp500.Close, length=ma_length)
    return sp500

def sp500_bbands(start_date,
                 bbands_length = 20,
                 bbands_std = 2):
    sp500 = generate_sp500(start_date)
    my_bbands = ta.bbands(close = sp500.Close, length=bbands_length, std=bbands_std)
    # maybe look into renaming bbands if necessary
    sp500 = sp500.join(my_bbands)
    return sp500

@st.cache_data
def generate_3mrx(start_date, end_date, interval = '1d'):
    r03m = yf.download(['^IRX'],
                       start_date,
                       end_date,
                       interval)
    r03m.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close', 'Stock Splits', 'Dividends'], axis=1, inplace=True)
    r03m.rename(columns = {"Close": "3mClose"}, inplace=True)
    r03m['ST % Change'] = r03m['3mClose'].pct_change()

    return r03m

@st.cache_data
def generate_10yrx(start_date, end_date, interval = '1d'):
    r10y = yf.download(['^TNX'],
                       start_date,
                       end_date,
                       interval)
    r10y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close', 'Stock Splits', 'Dividends'], axis=1, inplace=True)
    r10y.rename(columns = {"Close": "10yClose"}, inplace=True)
    r10y['LT % Change'] = r10y['10yClose'].pct_change()

    return r10y

@st.cache_data
def generate_30yrx(start_date, end_date, interval = '1d'):
    r30y = yf.download(['^TYX'],
                       start_date,
                       end_date,
                       interval)
    r30y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close', 'Stock Splits', 'Dividends'], axis=1, inplace=True)
    r30y.rename(columns = {"Close": "30yClose"}, inplace=True)
    r30y['LT % Change'] = r30y['30yClose'].pct_change()

    return r30y

@st.cache_data
def yield_diff(start_date, end_date, lt_yield_inp = '30y', interval = '1d'):
    
    #LONG-TERM YIELD GENERATION
    if lt_yield_inp == '30y':
        lt_yield = generate_30yrx(start_date, end_date, interval)
        lt_yield.rename(columns={'30yClose': 'Long Term Yield'}, inplace=True)
    elif lt_yield_inp == '10y':
        lt_yield = generate_10yrx(start_date, end_date)
        lt_yield.rename(columns={'10yClose': 'Long Term Yield'}, inplace=True)
    
    #SHORT TERM YIELD GENERATION
    st_yield = generate_3mrx(start_date, end_date, interval)
    st_yield.rename(columns={'3mClose': 'Short Term Yield'}, inplace=True)

    #CALCULATING YIELD FIGURES
    dt_yield_diff = pd.concat([lt_yield, st_yield], axis = 1)
    dt_yield_diff['Yield Ratio'] = dt_yield_diff['Long Term Yield'] - dt_yield_diff['Short Term Yield']
    dt_yield_diff['Yield Ratio % Chg'] = dt_yield_diff['Yield Ratio'].pct_change()

    #OUTPUTTING VALUES
    curr_yielddiff = round(dt_yield_diff['Yield Ratio'].iloc[-1],2)
    curr_ltyield = round(dt_yield_diff['Long Term Yield'].iloc[-1],2)
    curr_styield = round(dt_yield_diff['Short Term Yield'].iloc[-1],2)
    
    return dt_yield_diff, curr_yielddiff, curr_ltyield, curr_styield