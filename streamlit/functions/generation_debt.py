import yfinance as yf
import pandas_ta as ta
import pandas as pd
import polars as pl
import streamlit as st
from fredapi import Fred

import sys
sys.path.append(".")

class Generate_Yield():
    def __init__(self):
        self.db = None
        self.yielddiff_lf = None
        self.maturity_options = {
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
        }

    def get_database(self, selection: str, start_date, end_date, frequency):
        '''
        Provide bond yield maturity length, start and end dates, and frequency 
        
        Args:
        selection: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        frequency: str -> Daily, Weekly, Monthly
        start_date: str -> 2023-01-01
        end_date: str -> 2023-12-31

        Output:
        '''
        # fred_key = st.secrets[fred_API_key]
        frequency_options = {"Daily": "d", "Weekly": "w", "Monthly": "m"}
        fred = Fred(api_key=st.secrets["fred_API_key"].FRED_API_KEY)
        pd_df = fred.get_series(self.maturity_options.get(selection), start_date, end_date, frequency=frequency_options.get(frequency)).reset_index()
        df = pl.LazyFrame(pd_df)
        df = df.drop_nulls()
        
        df = df.with_columns(pl.col("index")
                            .cast({'index': pl.Date})
                            ).drop_nulls()
        
        df = df.rename({"0":f"{selection} Rate", "index": "Date"})
        print(df.describe())
        # df = df.cast({'index': pl.Date})
        #                 "index": "Date"})
        return df

    def generate_yield_spread(self, start_date, end_date, frequency, numerator, denominator):
        '''
        Provide two selections of 2 different maturity terms, to return a LazyFrame with a spread between the two.
        Typically the longer yield term is in the numerator.

        Args:
        numerator: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        denominator: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        frequency: str -> Daily, Weekly, Monthly
        start_date: str -> 2023-01-01
        end_date: str -> 2023-12-31
        '''
        lf_numerator = self.get_database(numerator, start_date, end_date, frequency)
        lf_denominator = self.get_database(denominator, start_date, end_date, frequency)
        self.yielddiff_lf = lf_numerator.join(lf_denominator, on="Date")
        self.yielddiff_lf = self.yielddiff_lf.with_columns((pl.col(f"{numerator} Rate") / pl.col(f"{denominator} Rate")).round(3).alias("Rate Spread"))
        self.yielddiff_lf = self.yielddiff_lf.with_columns(pl.col("Rate Spread").pct_change().alias("Spread % Change"))
        self.yielddiff_lf = self.yielddiff_lf.with_columns((pl.col("Spread % Change")*100).round(1))


class Generate_Yields():
    def __init__(self):
        self.db = None
        self.db_graph = None

        self.yield_ratio = None
        self.curr_yieldratio = None
        self.curr_ltyield = None
        self.curr_styield = None

        self.curr_yielddiff = None
        self.curr_yieldratio = None

    def generate_db(self, term_yield: str, start_date: str, end_date: str, interval: str = "1d"):
        """
        Provide the ticker for the term yield and generates a database; can either be:
        - 3 month: ^IRX
        - 10 year: ^TNX
        - 30 year: ^TYX
        """
        self.db = yf.download([term_yield], start_date, end_date, interval=interval)
        self.db_graph = self.db.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1)
        self.db_graph['% Change'] = self.db['Close'].pct_change()

        return self.db_graph
    
    def generate_yield_ratio(self, start_date, end_date, interval, numerator: str, denominator: str):
        """
        Provide a numerator that is either 3 month (^IRX) or 10 year (^TNX) and a denominator that is either 10 year (^TNX) or 30 year (^TYX), returns a ratio between the numerator and denominator in a database.
        """
        # Generating Short and Long-Term databases
        self.num_yield, self.den_yield = self.generate_db(term_yield=numerator, start_date=start_date, end_date=end_date, interval=interval), self.generate_db(term_yield=denominator, start_date=start_date, end_date=end_date, interval=interval)
        self.num_yield.rename(columns={'Close': "Short Term Yield"}, inplace=True)
        self.den_yield.rename(columns={'Close': "Long Term Yield"}, inplace=True)

        # Calculates Yield Figures
        self.yield_ratio = pd.concat([self.num_yield, self.den_yield], axis=1)
        self.yield_ratio['Yield Ratio'] = self.yield_ratio['Short Term Yield']/self.yield_ratio['Long Term Yield']
        self.yield_ratio['Yield Ratio % Chg'] = self.yield_ratio['Yield Ratio'].pct_change()

        # Value for UI
        self.curr_yieldratio = round(self.yield_ratio['Yield Ratio'].iloc[-1],2)
        self.curr_ltyield = round(self.yield_ratio['Long Term Yield'].iloc[-1],2)
        self.curr_styield = round(self.yield_ratio['Short Term Yield'].iloc[-1],2)

    def metric_vs_selection(self, comparison_type:str, comparator:str, selected_value, sp500:pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame):
        type_dicts = {
            "ratio vs selection": {
                "1st value": self.curr_yieldratio,
                "2nd value": selected_value,
                "1st col": self.yield_ratio['Yield Ratio'],
                "2nd col": selected_value
            }
        }
        if comparator == 'Greater than':
            self.boolean_comp = type_dicts[comparison_type]['1st value'] > type_dicts[comparison_type]['2nd value']

            filtered_database = self.yield_ratio[type_dicts[comparison_type]['1st col'] > type_dicts[comparison_type]['2nd col']]

        elif comparator == 'Less than':
            self.boolean_comp = type_dicts[comparison_type]['1st value'] < type_dicts[comparison_type]['2nd value']

            filtered_database = self.yield_ratio[type_dicts[comparison_type]['1st col'] < type_dicts[comparison_type]['2nd col']]

        else:
            return "Check comparator value, should be either p greater or lower"

        sp500.append(filtered_database)
        ndx.append(filtered_database)
        rus2k.append(filtered_database)        

        return sp500, ndx, rus2k
