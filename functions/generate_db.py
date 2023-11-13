import yfinance as yf
import pandas as pd

def generate_sp500(start_date, interval = "1d"):
    sp500 = yf.download(['^GSPC'],
                        start_date,
                        interval = interval)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    return sp500

def generate_rsp(start_date, interval = "1d"):
    rsp = yf.download(['RSP'],
                      start_date,
                      interval = interval)
    rsp = rsp.drop(["Adj Close"], axis=1)
    return rsp

def generate_ndx(start_date, interval = '1d'):
    ndx = yf.download(['^IXIC'],
                      start_date,
                      interval = interval)
    return ndx

def generate_rsp(start_date, interval ='1d'):
    rsp = yf.download(['RSP'],
                      start_date,
                      interval = interval)
    return rsp

def generate_vix(start_date, interval = '1d'):
    vix = yf.download(['^VIX'],
                      start_date,
                      interval = interval)
    vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return vix

def generate_3mrx(start_date, interval = '1d'):
    r03m = yf.download(['^IRX'],
                       start_date,
                       interval = interval)
    r03m.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r03m

def generate_10yrx(start_date, interval = '1d'):
    r10y = yf.download(['^TNX'],
                       start_date,
                       interval = interval)
    r10y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r10y

def generate_30yrx(start_date, interval = '1d'):
    r30y = yf.download(['^TYX'],
                       start_date,
                       interval = interval)
    r30y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r30y

def generate_hyg(start_date, interval = '1d'):
    hyg = yf.download(['HYG'],
                      start_date,
                      interval = interval)
    return hyg

def generate_energy(start_date, interval = '1d'):
    energy = yf.download(['XLE'],
                         start_date,
                         interval = interval)
    return energy

def generate_utility(start_date, interval = '1d'):
    utility = yf.download(['XLU'],
                          start_date,
                          interval = interval)
    return utility

def generate_consumer(start_date, interval = '1d'):
    consumer = yf.download(['XLY'],
                           start_date,
                           interval = interval)
    return consumer