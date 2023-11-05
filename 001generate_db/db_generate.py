import yfinance as yf


def generate_sp500(start_date):
    sp500 = yf.download(['^GSPC'], start_date)
    return sp500

def generate_vix(start_date):
    vix = yf.download(['^VIX'], start_date)
    return vix

def generate_2rx(start_date):
    r02 = yf.download(['IRX'], start_date)
    return r02

def generate_10rx(start_date):
    r10 = yf.download(['TNX'], start_date)
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
