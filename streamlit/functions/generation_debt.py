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
        frequency_options = {"Daily": "d", "Weekly": "w", "Monthly": "m"}
        fred_api = st.secrets.fred_api
        fred = Fred(api_key=fred_api)
        pd_df = fred.get_series(self.maturity_options.get(selection), start_date, end_date, frequency=frequency_options.get(frequency)).reset_index()
        l_df = pl.LazyFrame(pd_df)
        l_df = l_df.with_columns().drop_nulls().cast({'index': pl.Date})
        
        l_df = l_df.rename({"0":f"{selection} Rate", "index": "Date"})
        return l_df

    def generate_yield_spread(self, start_date, end_date, frequency, long_term_yield, short_term_yield) -> None:
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
        self.lf_ltyield = self.get_database(long_term_yield, start_date, end_date, frequency)
        self.lf_styield = self.get_database(short_term_yield, start_date, end_date, frequency)
        self.yielddiff_lf = self.lf_ltyield.join(self.lf_styield, on="Date")

        self.yielddiff_lf = (self.yielddiff_lf.with_columns(
            (pl.col(f"{long_term_yield} Rate") - pl.col(f"{short_term_yield} Rate")).alias('Rate Spread')
        ).select(
            pl.col('*'),
            (pl.col('Rate Spread').pct_change()*100).alias('% Change')
        ))


    def metric_vs_selection_cross(self, comparison_type: str, selected_value: tuple, sp500: pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame, comparator:str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        '''
        Provide comparison metrics and return back dates in the sp500, ndx, and rus2k DataFrames where these comparison logics were applied.

        Args:\n
        comparison_type: str -> current price, % change between\n
        selected_value: tuple -> range between two numbers, where the first number is the lower value\n
        comparator: str -> Greater than, Lower than, Between\n

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
                "db values": "% Change",
                "db values x": 100,
                "comparison value lower": comparison_value_lower,
                "comparison value higher": comparison_value_higher
            }
        }
        if comparator == 'Greater than':
            filtered_database = self.yielddiff_lf.filter(
                (pl.col(selection_dict[comparison_type]["db values"]) > comparison_value_lower) &
                (pl.col(selection_dict[comparison_type]["db values"]).shift(1) < comparison_value_lower)
            )
        elif comparator == 'Lower Than':
            filtered_database = self.yielddiff_lf.filter(
                (pl.col(selection_dict[comparison_type]["db values"]) < comparison_value_lower) &
                (pl.col(selection_dict[comparison_type]["db values"]).shift(1) > comparison_value_lower)
            )
        elif comparator == 'Between':
            filtered_database = self.yielddiff_lf.filter(
                (pl.col(selection_dict[comparison_type]["db values"]).is_between(comparison_value_lower, comparison_value_higher)) &
                ~(pl.col(selection_dict[comparison_type]["db values"]).shift(1).is_between(comparison_value_lower, comparison_value_higher))
            )
        sp500.append(filtered_database)
        ndx.append(filtered_database)
        rus2k.append(filtered_database)
        
        return sp500, ndx, rus2k


class Generate_Yield_panda():
    def __init__(self):
        self.db = None
        self.db_graph = None
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
        self.yield_ratio = None
        self.curr_yieldratio = None
        self.curr_ltyield = None
        self.curr_styield = None

        self.curr_yielddiff = None
        self.curr_yieldratio = None

    def get_database(self, selection: str, start_date, end_date, frequency):
        '''
        Provide bond yield maturity length, start and end dates, and frequency 
        
        Args:
        selection: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        frequency: str -> Daily, Weekly, Monthly
        start_date: str -> 2023-01-01
        end_date: str -> 2023-12-31

        Output:'''
        frequency_options = {"Daily": "d", "Weekly": "w", "Monthly": "m"}
        fred_api = st.secrets.fred_api
        fred = Fred(api_key=fred_api)
        return fred.get_series(self.maturity_options.get(selection), start_date, end_date, frequency=frequency_options.get(frequency))
    
    def generate_yield_spread(self, start_date, end_date, frequency, long_term_yield:str, short_term_yield:str) -> None:
        '''
        Provide two selections of 2 different maturity terms, to return a LazyFrame with a spread between the two.
        Typically the longer yield term is in the numerator.\n

        Args:
        long_term_yield: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        short_term_yield: str -> 1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y
        frequency: str -> Daily, Weekly, Monthly
        start_date: str -> 2023-01-01
        end_date: str -> 2023-12-31
        '''

        self.ltyield = self.get_database(long_term_yield, start_date, end_date, frequency)
        self.ltyield=pd.DataFrame(self.ltyield, columns=[f'{long_term_yield} Rate'])
        self.ltyield.index = pd.to_datetime(self.ltyield.index, format='%Y/%m/%d')

        self.styield = self.get_database(short_term_yield, start_date, end_date, frequency)
        self.styield = pd.DataFrame(self.styield, columns=[f'{short_term_yield} Rate'])
        self.styield.index = pd.to_datetime(self.styield.index, format='%Y/%m/%d')

        self.yielddiff_df = pd.concat([self.ltyield, self.styield], axis=1)
        
        # Calculate yield spread (lt - st)
        self.yielddiff_df['Rate Spread'] = self.yielddiff_df[f'{long_term_yield} Rate'] - self.yielddiff_df[f'{short_term_yield} Rate']
        self.yielddiff_df['% Change'] = self.yielddiff_df['Rate Spread'].pct_change()*100


    def metric_vs_selection_cross(self, comparison_type: str, selected_value: list, sp500: pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame, comparator:str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        '''
        Provide comparison metrics and return back dates in the sp500, ndx, and rus2k DataFrames where these comparison logics were applied.

        Args:\n
        comparison_type: str -> current price, % change between\n
        selected_value: list -> range between two numbers, where the first number is the lower value\n
        comparator: str -> Greater than, Lower than, Between\n

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
                "current db value": self.yielddiff_df['Rate Spread'][-1],
                "db values": "Rate Spread",
                "db values x": 1,
                "comparison value lower": comparison_value_lower,
                "comparison value higher": 0
            },
            "% change between": {
                "current db value": self.yielddiff_df['% Change'][-1],
                "db values": "% Change",
                "db values x": 100,
                "comparison value lower": comparison_value_lower,
                "comparison value higher": comparison_value_higher
            }
        }
        print(f'Selected value: {selected_value[0]}')
        print(f'')
        if comparator == 'Greater than':
            filtered_database = self.yielddiff_df[
                (self.yielddiff_df[selection_dict[comparison_type]["db values"]] > comparison_value_lower) &
                (self.yielddiff_df[selection_dict[comparison_type]["db values"]].shift(1) <= comparison_value_lower)
            ]
        elif comparator == 'Lower Than':
            filtered_database = self.yielddiff_df[
                (self.yielddiff_df[selection_dict[comparison_type]["db values"]] < comparison_value_lower) &
                (self.yielddiff_df[selection_dict[comparison_type]["db values"]].shift(1) >= comparison_value_lower)
            ]
        elif comparator == 'Between':
            filtered_database = self.yielddiff_df[
                (self.yielddiff_df[selection_dict[comparison_type]["db values"]].between(comparison_value_lower, comparison_value_higher)) &
                ~ (self.yielddiff_df[selection_dict[comparison_type]["db values"]].shift(1).between(comparison_value_lower, comparison_value_higher))
            ]
        sp500.append(filtered_database)
        ndx.append(filtered_database)
        rus2k.append(filtered_database)
        print(filtered_database)
        
        return sp500, ndx, rus2k
