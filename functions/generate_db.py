import yfinance as yf

def generate_sp500(start_date):
    sp500 = yf.download(['^GSPC'], start_date)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    return sp500

def generate_rsp(start_date):
    rsp = yf.download(['RSP'], start_date)
    rsp = rsp.drop(["Adj Close"], axis=1)
    return rsp

def generate_ndx(start_date):
    ndx = yf.download(['^IXIC'], start_date)
    return ndx

def generate_rsp(start_date):
    rsp = yf.download(['RSP'], start_date)
    return rsp

def generate_vix(start_date):
    vix = yf.download(['^VIX'], start_date)
    vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return vix

def generate_3mrx(start_date):
    r03m = yf.download(['^IRX'], start_date)
    r03m.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r03m

def generate_10yrx(start_date):
    r10y = yf.download(['^TNX'], start_date)
    r10y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r10y

def generate_30yrx(start_date):
    r30y = yf.download(['^TYX'], start_date)
    r30y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    return r30y

def generate_hyg(start_date):
    hyg = yf.download(['HYG'], start_date)
    return hyg

def generate_energy(start_date):
    energy = yf.download(['XLE'], start_date)
    return energy

def generate_utility(start_date):
    utility = yf.download(['XLU'], start_date)
    return utility

def generate_consumer(start_date):
    consumer = yf.download(['XLY'], start_date)
    return consumer

