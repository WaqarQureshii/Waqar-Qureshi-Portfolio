import yfinance as yf
import pandas_ta as ta
import pandas as pd
import streamlit as st

import math

class Generate_DB:
    def __init__(self):
        """
        Generates database with all of its metrics by providing it parameters.

        Arguments
        ----------
        ticker (str): Provide a ticker symbol.
            SP500 = ^GSPC\n
            S&P Energy = XLE\n
            S&P Utility = XLU\n
            S&P Consumer = XLY\n
            RSP = RSP\n
            Nasdaq = ^IXIC\n
            Russel 2000 = ^RUT\n
            VIX = ^VIX\n
            High Yield Corp Bond = HYG\n
        """
        self.db = None
        self.curr_rsi = None
        self.curr_ma = None
        self.curr_p = None
        self.pctchg_int = None
        self.pctchg_str = None
        self.pctchg_floor_int = None
        self.pctchg_ceil_int = None
    
    def get_database(self, ticker: str, start_date: str, end_date: str, interval: str ="1d", rsi_value: int =22, ma_length: int = 50):
        self.db = yf.download([ticker], start=start_date, end=end_date, interval=interval)
        
        # Database Massage
        self.db['% Change'] = self.db['Close'].pct_change()

        # (-) Columns
        self.db = self.db.drop(['Adj Close'], axis=1)
        self.db['rsi'] = ta.rsi(close = self.db.Close, length=rsi_value)
        self.db['ma'] = ta.sma(close = self.db.Close, length=ma_length)
        
        # (+) % Change
        self.pctchg_int = self.db["% Change"].iloc[-1] # % Change COLUMN
        self.pctchg_str = "{:.2%}".format(self.db["% Change"].iloc[-1]) # %Change current value
        # ---% Change FLOOR & CEILING
        self.pctchg_floor_int = math.floor(self.pctchg_int*100)/100
        self.pctchg_ceil_int = math.ceil(self.pctchg_int*100)/100
        
        # (+) RSI
        self.curr_rsi = self.db['rsi'].iloc[-1]
        # self.curr_rsi = int(self.db['rsi'].iloc[-1])

        # (+) Moving Average
        self.curr_ma = int(self.db['ma'].iloc[-1])

        # get Current Price
        self.curr_p = int(self.db["Close"].iloc[-1])

    def metric_vs_selection(self, comparison_type:str, comparator:str, selected_value, sp500:pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame):
        '''
        Compares the current level price with the selected value.

        Args:
        comparison_type: 'current price', '% change', 'price vs ma'
        comparator: 'Greater than', 'Less than'

        Output:
        self, sp500_intersection, ndx_intersection, rus2k_intersection
        '''
        ref_dict = {
            "current price": {
                "1st value": self.curr_p,
                "2nd value": selected_value,
                "1st col": self.db["Close"],
                "2nd col": selected_value,
                "1st multiplier": 1
            },
            "% change": {
                "1st value": self.pctchg_int*100,
                "2nd value": selected_value,
                "1st col": self.db["% Change"]*100,
                "2nd col": selected_value,
                "1st multiplier": 100
            },
            "price vs ma": {
                "1st value": self.curr_p,
                "2nd value": self.curr_ma,
                "1st col": self.db["Close"],
                "2nd col": self.db['ma'],
                "1st multiplier": 1
            }
        }

        if comparator == 'Greater than':
            self.boolean_comp = ref_dict[comparison_type]['1st value'] > ref_dict[comparison_type]['2nd value']

            filtered_database = self.db[ref_dict[comparison_type]['1st col'] > ref_dict[comparison_type]['2nd col']]

        elif comparator == 'Less than':
            self.boolean_comp = ref_dict[comparison_type]['1st value'] < ref_dict[comparison_type]['2nd value']

            filtered_database = self.db[ref_dict[comparison_type]['1st col'] < ref_dict[comparison_type]['2nd col']]

        else:
            return "Check comparator value, should be either p greater or lower"

        sp500.append(filtered_database)
        ndx.append(filtered_database)
        rus2k.append(filtered_database)        

        return sp500, ndx, rus2k

    
class Generate_Yield():
    def __init__(self, start_date: str, end_date: str, interval: str = "1d"):
        self.db = None
        self.db_graph = None

        self.yield_ratio = None
        self.curr_yieldratio = None
        self.curr_ltyield = None
        self.curr_styield = None

        self.curr_yielddiff = None

        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

    def generate_db(self, term_yield: str):
        """
        Provide the ticker for the term yield and generates a database; can either be:
        - 3 month: ^IRX
        - 10 year: ^TNX
        - 30 year: ^TYX
        """
        self.db = yf.download([term_yield], self.start_date, self.end_date, interval=self.interval)
        self.db_graph = self.db.drop(["Volume", 'Open', 'High', 'Low', 'Adj Close'], axis=1)
        self.db_graph['% Change'] = self.db['Close'].pct_change()

        return self.db_graph
    
    def calc_yield_curve(self, numerator: str, denominator: str):
        """
        Provide a numerator that is either 3 month (^IRX) or 10 year (^TNX) and a denominator that is either 10 year (^TNX) or 30 year (^TYX), returns a ratio between the numerator and denominator in a database.
        """
        # Generating Short and Long-Term databases
        self.num_yield, self.den_yield = self.generate_db(numerator), self.generate_db(denominator)
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

        return self
    
    def calc_yield_diff(self, numerator: str, denominator: str):
        """
        Provide a numerator that is either 3 month (^IRX) or 10 year (^TNX) and a denominator that is either 10 year (^TNX) or 30 year (^TYX), returns a ratio between the numerator and denominator in a database.
        """
        # Generating Short and Long-Term databases
        self.num_diff, self.den_diff = self.generate_db(numerator), self.generate_db(denominator)
        self.num_diff.rename(columns={'Close': "Short Term Yield"}, inplace=True)
        self.den_diff.rename(columns={'Close': "Long Term Yield"}, inplace=True)

        # Calculates Yield Figures
        self.yield_diff = pd.concat([self.num_diff, self.den_diff], axis=1)
        self.yield_diff['Yield Diff'] = self.yield_diff['Long Term Yield'] - self.yield_diff['Short Term Yield']
        self.yield_diff['Yield Diff % Chg'] = self.yield_diff['Yield Diff'].pct_change()

        # Value for UI
        self.curr_yielddiff = round(self.yield_diff['Yield Diff'].iloc[-1],2)
        self.curr_ltyield = round(self.yield_diff['Long Term Yield'].iloc[-1],2)
        self.curr_styield = round(self.yield_diff['Short Term Yield'].iloc[-1],2)

        return self

    def calc_diffgreater(self, selected_value, sp500intersection, ndxintersection, rus2kintersection):

        self.Boolean = self.curr_yielddiff >= selected_value
        filtered_database = self.yield_diff[self.yield_diff['Yield Diff'] <= selected_value]
        
        sp500intersection.append(filtered_database)
        ndxintersection.append(filtered_database)
        rus2kintersection.append(filtered_database)

        return sp500intersection, ndxintersection, rus2kintersection
