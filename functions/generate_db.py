import yfinance as yf

def generate_sp500(start_date):
    sp500 = yf.download(['^GSPC'], start_date)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    return sp500

sp500 = generate_sp500('2008-01-01')
print(sp500)

def generate_ndx(start_date):
    ndx = yf.download(['^IXIC'], start_date)
    return ndx

def generate_rsp(start_date):
    rsp = yf.download(['RSP'], start_date)
    return rsp

def generate_vix(start_date):
    vix = yf.download(['^VIX'], start_date)
    vix = vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1)
    return vix

def generate_2rx(start_date):
    r02 = yf.download(['^IRX'], start_date)
    return r02

def generate_10rx(start_date):
    r10 = yf.download(['^TNX'], start_date)
    return r10

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

