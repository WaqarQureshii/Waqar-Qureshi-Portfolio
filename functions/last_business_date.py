import pandas as pd
from datetime import datetime, timedelta

def last_biz_date():
    today = datetime.today()
    last_biz_day = pd.date_range(end=today - timedelta(days=1), periods=1, freq='B')[0]
    return last_biz_day

def today_date():
    today = datetime.today()
    # last_biz_day = pd.date_range(end=today, periods=1, freq='B')[0]
    return today_date