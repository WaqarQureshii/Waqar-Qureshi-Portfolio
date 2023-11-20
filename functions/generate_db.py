import yfinance as yf

def generate_sp500(start_date, interval = "1d"):
    sp500 = yf.download(['^GSPC'],
                        start_date,
                        interval = interval)
    sp500 = sp500.drop(["Adj Close"], axis=1)
    
    sp500['% Change'] = sp500['Close'].pct_change()
    
    return sp500


def generate_rsp(start_date, interval = "1d"):
    rsp = yf.download(['RSP'],
                      start_date,
                      interval = interval)
    rsp = rsp.drop(["Adj Close"], axis=1)

    rsp['% Change'] = rsp['Close'].pct_change()
    
    return rsp


def generate_ndx(start_date, interval = '1d'):
    ndx = yf.download(['^IXIC'],
                      start_date,
                      interval = interval)
    ndx = ndx.drop(["Adj Close"], axis=1)

    ndx['% Change'] = ndx['Close'].pct_change()
    
    return ndx


def generate_vix(start_date, end_date, interval = '1d'):
    vix = yf.download(['^VIX'],
                      start_date,
                      end_date,
                      interval = interval)
    vix.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)

    vix['% Change'] = vix['Close'].pct_change()

    return vix


def generate_3mrx(start_date, interval = '1d'):
    r03m = yf.download(['^IRX'],
                       start_date,
                       interval = interval)
    r03m.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r03m['% Change'] = r03m['Close'].pct_change()

    return r03m


def generate_10yrx(start_date, interval = '1d'):
    r10y = yf.download(['^TNX'],
                       start_date,
                       interval = interval)
    r10y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r10y['% Change'] = r10y['Close'].pct_change()

    return r10y


def generate_30yrx(start_date, interval = '1d'):
    r30y = yf.download(['^TYX'],
                       start_date,
                       interval = interval)
    r30y.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1, inplace=True)
    
    r30y['% Change'] = r30y['Close'].pct_change()

    return r30y


def generate_hyg(start_date, interval = '1d'):
    hyg = yf.download(['HYG'],
                      start_date,
                      interval = interval)
    
    hyg['% Change'] = hyg['Close'].pct_change()

    return hyg


def generate_energy(start_date, interval = '1d'):
    energy = yf.download(['XLE'],
                         start_date,
                         interval = interval)
    
    energy['% Change'] = energy['Close'].pct_change()
    
    return energy


def generate_utility(start_date, interval = '1d'):
    utility = yf.download(['XLU'],
                          start_date,
                          interval = interval)
    
    utility['% Change'] = utility['Close'].pct_change()
    
    return utility


def generate_consumer(start_date, interval = '1d'):
    consumer = yf.download(['XLY'],
                           start_date,
                           interval = interval)
    
    consumer['% Change'] = consumer['Close'].pct_change()
    
    return consumer