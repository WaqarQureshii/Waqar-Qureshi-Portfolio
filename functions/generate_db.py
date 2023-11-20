import yfinance as yf
import pandas_ta as ta
import pandas as pd

def generate_sp500(start_date, end_date, interval = "1d"):
    sp500 = yf.download(['^GSPC'],
                        start_date,
                        end_date,
                        interval = interval)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    
    sp500['% Change'] = sp500['Close'].pct_change()
    
    return sp500


def generate_rsp(start_date, end_date, interval = "1d"):
    rsp = yf.download(['RSP'],
                      start_date,
                      end_date,
                      interval = interval)
    rsp = rsp.drop(["Adj Close"], axis=1)

    rsp['% Change'] = rsp['Close'].pct_change()
    
    return rsp


def generate_ndx(start_date, end_date, interval = '1d'):
    ndx = yf.download(['^IXIC'],
                      start_date,
                      end_date,
                      interval = interval)
    ndx = ndx.drop(["Adj Close"], axis=1)

    ndx['% Change'] = ndx['Close'].pct_change()
    
    return ndx


def generate_vix(start_date, end_date, interval = '1d'):
    vix = yf.download(['^VIX'],
                      start_date,
                      end_date,
                      interval)
    vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)

    vix['% Change'] = vix['Close'].pct_change()

    return vix


def generate_3mrx(start_date, end_date, interval = '1d'):
    r03m = yf.download(['^IRX'],
                       start_date,
                       end_date,
                       interval = interval)
    r03m.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r03m['% Change'] = r03m['Close'].pct_change()

    return r03m


def generate_10yrx(start_date, end_date, interval = '1d'):
    r10y = yf.download(['^TNX'],
                       start_date,
                       end_date,
                       interval = interval)
    r10y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r10y['% Change'] = r10y['Close'].pct_change()

    return r10y


def generate_30yrx(start_date, end_date, interval = '1d'):
    r30y = yf.download(['^TYX'],
                       start_date,
                       end_date,
                       interval = interval)
    r30y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r30y['% Change'] = r30y['Close'].pct_change()

    return r30y


def generate_hyg(start_date, end_date, interval = '1d'):
    hyg = yf.download(['HYG'],
                      start_date,
                      end_date,
                      interval = interval)
    
    hyg['% Change'] = hyg['Close'].pct_change()

    return hyg


def generate_energy(start_date, end_date, interval = '1d'):
    energy = yf.download(['XLE'],
                         start_date,
                         end_date,
                         interval = interval)
    
    energy['% Change'] = energy['Close'].pct_change()
    
    return energy


def generate_utility(start_date, end_date, interval = '1d'):
    utility = yf.download(['XLU'],
                          start_date,
                          end_date,
                          interval = interval)
    
    utility['% Change'] = utility['Close'].pct_change()
    
    return utility


def generate_consumer(start_date, end_date, interval = '1d'):
    consumer = yf.download(['XLY'],
                           start_date,
                           end_date,
                           interval = interval)
    
    consumer['% Change'] = consumer['Close'].pct_change()
    
    return consumer

def nasdaqvssp500(start_date, interval = '1d'):
    nasdaq = generate_ndx(start_date, interval=interval)
    nasdaq.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    nasdaq.rename(columns={'Close':'Nasdaq Close'}, inplace=True)

    sp500 = generate_sp500(start_date, interval=interval)
    sp500.drop(['Open', 'High', 'Low', 'Volume', '% Change'], axis = 1, inplace=True)
    sp500.rename(columns={'Close':'SP500 Close'}, inplace=True)

    ndxvssp500 = pd.concat([nasdaq, sp500], axis=1)
    ndxvssp500['Nasdaq vs SP500 Ratio'] = ndxvssp500['Nasdaq Close']/ndxvssp500['SP500 Close']
    ndxvssp500.drop(['Nasdaq Close', 'SP500 Close'], axis = 1, inplace=True)
    
    return ndxvssp500


def sp500_rsi(start_date,
              end_date,
              rsi_value = 22,
              interval = '1d'):
    sp500 = generate_sp500(start_date, end_date, interval = interval)
    sp500[f'rsi'] = ta.rsi(close = sp500.Close, length=rsi_value)
    return sp500


def sp500_bbands(start_date,
                 bbands_length = 20,
                 bbands_std = 2):
    sp500 = generate_sp500(start_date)
    my_bbands = ta.bbands(close = sp500.Close, length=bbands_length, std=bbands_std)
    # maybe look into renaming bbands if necessary
    sp500 = sp500.join(my_bbands)
    return sp500


def yield_difference(start_date, lt_yield_inp = '30y'):
    #LONG-TERM YIELD GENERATION
    if lt_yield_inp == '30y':
        lt_yield = generate_30yrx(start_date)
    else:
        lt_yield = generate_10yrx(start_date)
    lt_yield.rename(columns={'Close': 'Long Term Yield'}, inplace=True)
    #SHORT TERM YIELD GENERATION
    
    st_yield = generate_3mrx(start_date)
    st_yield.rename(columns={'Close': 'Short Term Yield'}, inplace=True)

    #CALCULATING YIELD DIFFERENCE
    dt_yield_diff = pd.concat([lt_yield, st_yield], axis = 1)
    dt_yield_diff['Yield Difference'] = dt_yield_diff['Long Term Yield'] - dt_yield_diff['Short Term Yield']
    return dt_yield_diff