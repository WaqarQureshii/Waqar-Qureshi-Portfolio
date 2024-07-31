import yfinance as yf
import pandas_ta as ta
import pandas as pd
import polars as pl
import streamlit as st
from fredapi import Fred

import sys
sys.path.append(".")
import fred_api_key

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
        fred = Fred(api_key=fred_api_key.key)
        pd_df = fred.get_series(self.maturity_options.get(selection), start_date, end_date, frequency=frequency_options.get(frequency)).reset_index()
        l_df = pl.LazyFrame(pd_df)
        l_df = l_df.with_columns().drop_nulls().cast({'index': pl.Date})
        
        l_df = l_df.rename({"0":f"{selection} Rate", "index": "Date"})
        return l_df

    def generate_yield_spread(self, start_date, end_date, frequency, numerator, denominator) -> None:
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
        self.yielddiff_lf.with_columns(
            (
            (pl.col(F"{numerator} Rate") / pl.col(F"{denominator} Rate"))
                .round(3).alias("Rate Spread")
            ),
            (
            (pl.col("Rate Spread").pct_change().alias("Spread % Change"))*100
             )
                .round(1)
        )

    def metric_vs_selection_cross(self, comparison_type: str, selected_value: tuple, sp500: pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame, comparator:str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        '''
        Provide comparison metrics and return back dates in the sp500, ndx, and rus2k DataFrames where these comparison logics were applied.

        Args:
        comparison_type: str -> current price, % change between
        selected_value: tuple -> range between two numbers, where the first number is the lower value
        comparator: str -> Greater than, Lower than, Between

        Output:
        self, sp500_intersection, ndx_intersection, rus2k_intersection
        '''
        
        if len(selected_value)==2:
            comparison_value_lower = selected_value[0]
            comparison_value_higher = float(selected_value[1])
        elif len(selected_value)==1:
            comparison_value_lower = selected_value[0]
            comparison_value_higher = None
        elif len(selected_value)==0:
            comparison_value_lower = None
            comparison_value_higher = None
        else:
            comparison_value_higher=None

        selection_dict = {
            "current price": {
                "current db value": self.yielddiff_lf.select(pl.last("Rate Spread")),
                "db values": "Rate Spread",
                "db values x": 1,
                "comparison value lower": comparison_value_lower,
                "comparison value higher": 0
            },
            "% change between": {
                "current db value": self.yielddiff_lf.select(pl.last("Spread % Change")),
                "db values": "Spread % Change",
                "db values x": 100,
                "comparison value lower": comparison_value_lower,
                "comparison value higher": comparison_value_higher
            }
        }

        if comparator =='Greater than':
            try: #TODO build logic that isn't row-by-row.
                pass
            except:
                pass


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
