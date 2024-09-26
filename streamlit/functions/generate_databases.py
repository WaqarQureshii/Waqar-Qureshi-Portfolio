import yfinance as yf
import polars as pl
import polars_talib as plta
import streamlit as st
from fredapi import Fred

from functools import reduce

    # def generate_common_dates(self, intersection_dbs:list, selected_returninterval:int):
    #     appended_dates = [df.index for df in intersection_dbs]
    #     if appended_dates:
    #         unique_dates = reduce(lambda left,right: left.intersection(right), appended_dates).to_list()

    #         self.db['% Change Sel Interval'] = self.db['Close'].pct_change(selected_returninterval).shift(-selected_returninterval)

    #         self.common_dates = self.db[self.db.index.isin(unique_dates)]

    #         self.avg_return = self.common_dates['% Change Sel Interval'].mean()
    #         self.no_of_occurrences = len(self.common_dates['% Change Sel Interval'])
    #         self.no_of_positives = (self.common_dates['% Change Sel Interval'] > 0).sum()
    #         positive_percentage = self.no_of_positives/self.no_of_occurrences
    #         self.positive_percentage = '{:.2%}'.format(positive_percentage)

class Generate_Equity:
    def __init__(self):
        self.db=None
    
    def get_database(self, ticker: list[str], start_date: str, end_date: str, interval: str="1d", rsi_value: int=22, ma_length: int=50):
        """
        Generates database with all of its metrics by providing it parameters.

        Arguments
        ----------
        ticker list[str]: Provide a ticker symbol.
            SP500 = ^GSPC\n
            S&P Energy = XLE\n
            S&P Utility = XLU\n
            S&P Consumer = XLY\n
            RSP = RSP\n
            Nasdaq = ^IXIC\n
            Russel 2000 = ^RUT\n
            VIX = ^VIX\n
            High Yield Corp Bond = HYG\n

        interval (str): Provide a timeframe to run database on.
            1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo\n
        
        rsi_value (int): Provide a timeframe to calculate the Relative Strength Index (RSI)
            \n
        ma_length (int): Provide a timeframe to calculate the Moving Average (MA)
            \n
        """

        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        df['Date'] = df.index
        self.lf = pl.LazyFrame(df).select(
            pl.col("*").exclude("Adj Close")
            ).cast(
                {"Date": pl.Date}
                ).select(['Date', 'Open', 'High', 'Low', 'Close', 'Volume']).with_columns(
                    (pl.col("Close").pct_change()*100).alias("% Change"),
                    (plta.rsi(pl.col("Close"), timeperiod=rsi_value)).alias("rsi"),
                    (plta.ma(pl.col("Close"), timeperiod=ma_length)).alias("ma")
                )
    
    def generate_ratio(self, numerator:str, denominator:str, start_date:str, end_date:str, interval:str, rsi_length:int=22, ma_length:int=50):
        """
        Generates a ratio column in the self.lf

        Arguments:
        ----------
        numerator (str): Nasdaq, S&P 500, Russell 2000, S&P 500 Equal Weight\n

        denominator (str): Nasdaq, S&P 500, Russell 2000, S&P 500 Equal Weight\n

        interval (str): 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo\n
        """

        ticker_dict = {
            "Nasdaq": "^IXIC",
            "S&P 500": "^GSPC",
            "Russell 2000": "^RUT",
            "S&P 500 Equal Weight": "RSP"
        }
        
        # --- Numerator generation ---
        numerator_cls = Generate_Equity()
        numerator_cls.get_database(ticker=ticker_dict.get(numerator, numerator),
                                   start_date=start_date,
                                   end_date=end_date,
                                   interval=interval)
        numerator_cls.lf=numerator_cls.lf.select(
            ["Date", "Close"]).rename(
                {"Close": f"{numerator} Close"}
            )
        
        # --- Denominator generation ---
        denominator_cls = Generate_Equity()
        denominator_cls.get_database(ticker=ticker_dict.get(denominator, denominator),
                                   start_date=start_date,
                                   end_date=end_date,
                                   interval=interval)
        denominator_cls.lf=denominator_cls.lf.select(
            ["Date", "Close"]).rename(
                {"Close": f"{denominator} Close"}
            )
        
        # --- Create Ratio Columns
        self.lf = numerator_cls.lf.join(denominator_cls.lf, on="Date").with_columns(
            (( pl.col(f"{numerator} Close") / pl.col(f"{denominator} Close")).alias("Close"))
        )
        self.lf = self.lf.with_columns(
            ((pl.col("Close").pct_change()*100).round(2)).alias("% Change")
        )

    def metric_vs_selection_cross(self, comparison_type: str, comparator: str, selected_value: list = None) -> tuple[pl.LazyFrame, pl.LazyFrame, pl.LazyFrame]:
        """
        Provide inputs related to different comparison types that filter out the indices filtered by the comparison types fed into it.

        Arguments
        ----------
        comparison_type (str): Provide the various types of comparison types.
            current_price\n
            %_change\n
            price_vs_ma\n
            rsi_vs_selection\n
            ratio%_changevsselection\n
            yield_spread\n
            
        comparator (str): Provide the comparator to compare against the selection.
            Greater than\n
            Less than\n
            Between
        """
        

        type_dict = {
            "current_price": {
                "db_column": "Close",
                "multiplier": 1,
                "comparison": selected_value
            },
            "%_change": {
                "db_column": "% Change",
                "multiplier": 100,
                "comparison": selected_value
            },
            "price_vs_ma": {
                "db_column": "Close",
                "multiplier": 1,
                "comparison_column": "ma"
            },
            "rsi_vs_selection":{
                "db_column": "rsi",
                "multiplier":1,
                "comparison": selected_value
            },
            "yield_spread":{
                "db_column": "Rate Spread",
                "multiplier":1,
                "comparison":selected_value
            },
            "US FED FUNDS":{
                "db_column": "US FED FUNDS Rate",
                "multiplier": 1,
                "comparison":selected_value
            }
        }

        if selected_value is None: # no selected values - this occurs when it's a value vs another value (Moving Average, for example)
            current_comparison, prior_comparison = [pl.col(type_dict[comparison_type]['comparison_column'])], [pl.col(type_dict[comparison_type]['comparison_column']).shift(1)]
        else:
            selected_value.sort()
            current_comparison, prior_comparison = selected_value, selected_value

        if comparator=='Greater than':
            filtered_db = self.lf.filter(
                (pl.col(type_dict[comparison_type]["db_column"]) > current_comparison[0]) &
                (pl.col(type_dict[comparison_type]["db_column"]).shift(1) <= prior_comparison[0])
            )
        elif comparator=='Less than':
            filtered_db = self.lf.filter(
                (pl.col(type_dict[comparison_type]["db_column"]) < current_comparison[0]) &
                (pl.col(type_dict[comparison_type]["db_column"]).shift(1) >= prior_comparison[0])
            )
        elif comparator=='Between':
            filtered_db=self.lf.filter(
                (pl.col(type_dict[comparison_type]["db_column"]).is_between(current_comparison[0], current_comparison[1])) &
                ~(pl.col(type_dict[comparison_type]["db_column"]).shift(1).is_between(prior_comparison[0], prior_comparison[1]))
            )
        self.filtered_dates = filtered_db.select("Date")

class Generate_Debt(Generate_Equity):
    def __init__(self):
        self.debt_instrument = {
            "1m": "DGS1MO",
            "3m": "DGS3MO",
            "6m": "DGS6MO",
            "1y": "DGS1",
            "2y": "DGS2",
            "3y": "DGS3",
            "5y": "DGS5",
            "7y": "DGS7",
            "10y": "DGS10",
            "20y": "DGS20",
            "30y": "DGS30",
            "US FED FUNDS": "EFFR"
        }

    def get_database(self, debt_instruments: str, start_date: str, end_date: str, frequency: str="Daily"):
        """
        Provide bond yield maturity length, start and end dates, and frequency 
        
        Arguments:
        ----------
        debt_instruments (str): Provide a length to maturity.
            1m\n
            3m\n
            6m\n
            1y\n
            2y\n
            3y\n
            5y\n
            7y\n
            10y\n
            20y\n
            30y\n
            US FED FUNDS\n

        frequency (str): Daily, Weekly, Monthly\n
        start_date (str): 2023-01-01\n
        end_date (str): 2023-12-31 
        """

        frequency_options = {"Daily": "d", "Weekly": "w", "Monthly": "m"}
        fred_api = st.secrets.fred_api
        fred = Fred(api_key=fred_api)
        pd_df = fred.get_series(self.debt_instrument.get(debt_instruments), start_date, end_date, frequency=frequency_options.get(frequency)).reset_index()
        self.lf = pl.LazyFrame(pd_df).with_columns().cast({'index': pl.Date}).rename({"0":f"{debt_instruments} Rate", "index": "Date"})

    def generate_yield_spread(self, start_date: str, end_date:str, long_term_yield:str, short_term_yield:str, frequency:str ="Daily"):
        """
        Creates a column that is a difference between two yields.

        Arguments
        ---------
        numerator (str): 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y\n
        denominator (str): 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y\n
        frequency (str): Daily, Weekly, Monthly\n
        start_date (str): 2023-01-01\n
        end_date (str): 2023-12-31
        """

        ltyield = Generate_Debt()
        ltyield.get_database(long_term_yield, start_date, end_date, frequency)
        styield = Generate_Debt()
        styield.get_database(short_term_yield, start_date, end_date, frequency)

        self.lf = ltyield.lf.join(styield.lf, on="Date")
        self.lf = (self.lf.with_columns(
            (pl.col(f"{long_term_yield} Rate") - pl.col(f"{short_term_yield} Rate")).alias('Rate Spread')
        ).select(
            pl.col('*'),
            (pl.col('Rate Spread').pct_change()*100).alias('% Change')
        ))

def filter_indices(db_list: list[pl.LazyFrame], sp500: pl.LazyFrame, ndx: pl.LazyFrame, rus2k: pl.LazyFrame) -> tuple[pl.LazyFrame, pl.LazyFrame, pl.LazyFrame]:
    """
    Returns a list of filtered LazyFrame objects based on common dates.

    Arguments
    ----------
    db_list (list[pl.LazyFrame]): List of LazyFrame databases.
    sp500 (pl.LazyFrame): LazyFrame for S&P 500.
    ndx (pl.LazyFrame): LazyFrame for Nasdaq.
    rus2k (pl.LazyFrame): LazyFrame for Russell 2000.
    """
    def get_common_dates_list():
        common_dates_df = reduce(lambda left, right: left.join(right, on="Date", how="inner"), db_list)
        common_dates_list = common_dates_df.select("Date").collect().get_column("Date").to_list()
        return common_dates_list
    
    def filter_indices(common_dates_list):
        return_indices = []
        if sp500 is not None:
            sp500_filtered = sp500.filter(pl.col("Date").is_in(common_dates_list)).select(["Date", "Close"])
            return_indices.append(sp500_filtered)
        if ndx is not None:
            ndx_filtered = ndx.filter(pl.col("Date").is_in(common_dates_list)).select(["Date", "Close"])
            return_indices.append(ndx_filtered)
        if rus2k is not None:
            rus2k_filtered = rus2k.filter(pl.col("Date").is_in(common_dates_list)).select(["Date", "Close"])
            return_indices.append(rus2k_filtered)
        return return_indices
    
    indices = filter_indices(get_common_dates_list())
    return indices