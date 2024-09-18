import yfinance as yf
import pandas_ta as ta
import pandas as pd
import polars as pl

import math
from functools import reduce

class Generate_DB:
    def __init__(self):
        self.db = None
        self.curr_rsi = None
        self.curr_ma = None
        self.curr_p = None
        self.pctchg_int = None
        self.pctchg_str = None
        self.pctchg_floor_int = None
        self.pctchg_ceil_int = None
    
    def get_database(self, ticker: str, start_date: str, end_date: str, interval: str ="1d", rsi_value: int =22, ma_length: int = 50): 
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
        self.curr_ma = (self.db['ma'].iloc[-1])

        # get Current Price
        self.curr_p = int(self.db["Close"].iloc[-1])

    def generate_ratio(self, numerator, denominator, start_date, end_date, interval, rsi_length:int=22, ma_length:int=50):
        '''
        Args:
        numerator or denominator: Nasdaq, S&P 500, Russel 2000, S&P 500 Equal Weight
        '''
        ticker_dict = {
            "Nasdaq": "^IXIC",
            "S&P 500": "^GSPC",
            "Russel 2000": "^RUT",
            "S&P 500 Equal Weight": "RSP"
        }

        numerator_cls = Generate_DB()
        numerator_ticker=ticker_dict.get(numerator)
        numerator_cls.get_database(ticker=numerator_ticker, start_date=start_date, end_date=end_date, interval=interval)
        numerator_cls.db.drop(['Open', 'High', 'Low', 'Volume', '% Change', 'ma', 'rsi'], axis = 1, inplace=True)
        numerator_cls.db.rename(columns={'Close': f'{numerator} Close'}, inplace=True)

        denominator_cls = Generate_DB()
        denominator_ticker=ticker_dict.get(denominator)
        denominator_cls.get_database(ticker=denominator_ticker, start_date=start_date, end_date=end_date, interval=interval)
        denominator_cls.db.drop(['Open', 'High', 'Low', 'Volume', '% Change', 'ma', 'rsi'], axis = 1, inplace=True)
        denominator_cls.db.rename(columns={'Close': f'{denominator} Close'},inplace=True)

        #Create Ratio Columns
        self.db = pd.concat([numerator_cls.db, denominator_cls.db], axis=1)
        self.db['Close']=self.db[f'{numerator} Close']/self.db[f'{denominator} Close']
        self.db['% Change']=(self.db['Close'].pct_change()*100).round(2)
        
        #Create rsi and ma columns
        self.db['rsi'] = ta.rsi(close = self.db['Close'], length=rsi_length)
        self.db['ma'] = ta.sma(close = self.db['Close'], length=ma_length)

        #Creating variables for UI
        self.curr_rsi = self.db['rsi'].iloc[-1]
        self.curr_ma = int(self.db['ma'].iloc[-1])
        self.curr_p = self.db['Close'].iloc[-1]
        self.pctchg_int = self.db['% Change'].iloc[-1]
        self.pctchg_str = "{:.2%}".format(self.pctchg_int / 100)

    def metric_vs_selection(self, comparison_type:str, comparator:str, selected_value, sp500:pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        '''
        Compares the current level price with the selected value.

        Args:
        comparison_type: current price, % change, price vs ma, rsi vs selection, ratio vs selection, ratio % change vs selection
        comparator: 'Greater than', 'Less than'

        Output:
        self, sp500_intersection, ndx_intersection, rus2k_intersection
        '''
        ref_dict = {
            "current price": {
                "1st value": self.curr_p,
                "2nd value": selected_value,
                "1st col": self.db.get("Close", 0),
                "2nd col": selected_value
            },
            "% change": {
                "1st value": self.pctchg_int*100,
                "2nd value": selected_value,
                "1st col": self.db.get("% Change", 0)*100,
                "2nd col": selected_value
            },
            "price vs ma": {
                "1st value": self.curr_p,
                "2nd value": self.curr_ma,
                "1st col": self.db.get("Close", 0),
                "2nd col": self.db['ma']
            },
            "rsi vs selection": {
                "1st value": self.curr_rsi,
                "2nd value": selected_value,
                "1st col": self.db.get("rsi", 0),
                "2nd col": selected_value
            },
            "ratio vs selection": {
                "1st value": self.curr_p,
                "2nd value": selected_value,
                "1st col": self.db.get("Ratio", 0),
                "2nd col": selected_value
            },
            "ratio % change vs selection": {
                "1st value": self.pctchg_int,
                "2nd value": selected_value,
                "1st col": self.db.get("Ratio % Chg", 0),
                "2nd col": selected_value
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

        sp500.append([filtered_database['Close']])
        ndx.append(filtered_database['Close'])
        rus2k.append(filtered_database['Close'])        

        return sp500, ndx, rus2k
    
    def metric_vs_comparison_cross(self, comparison_type:str, selected_value:tuple, sp500:pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame, comparator:str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        '''
        Compares the current level price with the selected value.

        Args:
        comparison_type: current price, % change, % change between, price vs ma, rsi vs selection, ratio vs selection, ratio % change vs selection
        comparator: 'Greater than', 'Less than', 'Between'

        Output:
        self, sp500_intersection, ndx_intersection, rus2k_intersection
        '''
        if len(selected_value) ==2:
            second_value = selected_value[0]
            third_value = float(selected_value[1])
        elif len(selected_value) == 1:
            second_value = selected_value[0]
            third_value = None
        elif len(selected_value) == 0:
            second_value = None
            third_value = None

        else: third_value = None
        ref_dict = {
            "current price": {
                "1st value": self.curr_p,
                "2nd value": second_value,
                "1st col": "Close",
                "1st col x": 1,
                "2nd col": second_value,
                "3rd col": 0
            },
            "% change": {
                "1st value": self.pctchg_int*100,
                "2nd value": second_value,
                "1st col": "% Change",
                "1st col x": 100,
                "2nd col": second_value,
                "3rd col": 0
            },
            "% change between": {
                "1st value": self.pctchg_int*100,
                "2nd value": second_value,
                "3rd value": third_value,
                "1st col": "% Change",
                "1st col x": 100,
                "2nd col": second_value,
                "3rd col": third_value
            },
            "price vs ma": {
                "1st value": self.curr_p,
                "2nd value": self.curr_ma,
                "1st col": "Close",
                "1st col x": 1,
                "2nd col": 'ma',
                "3rd col": 0
            },
            "rsi vs selection": {
                "1st value": self.curr_rsi,
                "2nd value": second_value,
                "1st col": "rsi",
                "1st col x": 1,
                "2nd col": second_value,
                "3rd col": 0
            },
            "ratio vs selection": {
                "1st value": self.curr_p,
                "2nd value": second_value,
                "1st col": "Ratio",
                "1st col x": 1,
                "2nd col": second_value,
                "3rd col": 0
            },
            "ratio % change vs selection": {
                "1st value": self.pctchg_int,
                "2nd value": second_value,
                "1st col": "Ratio % Chg",
                "1st col x": 1,
                "2nd col": second_value,
                "3rd col": 0
            }
        }

        # Initialize a variable to store the previous row's comparison result
        prev_comparison = False
        # Initialize an empty list to store the filtered rows
        filtered_rows = []
        for index, row in self.db.iterrows():
            # Check if the current row meets the existing condition
            if isinstance(ref_dict[comparison_type]['1st col'], str):
                column1 = row[ref_dict[comparison_type]['1st col']]*ref_dict[comparison_type]['1st col x']
            else:
                column1 = ref_dict[comparison_type]['1st col']

            if isinstance(ref_dict[comparison_type]['2nd col'], str):
                column2 = row[ref_dict[comparison_type]['2nd col']]
            else:
                column2 = ref_dict[comparison_type]['2nd col']

            if isinstance(ref_dict[comparison_type]['3rd col'], str):
                column3 = row[ref_dict[comparison_type]['3rd col']]
            elif isinstance(third_value, (float, int)):
                column3 = third_value
            else: column3 = None
            
            if comparator =='Greater than':
                try:
                    current_comparison = column1 > column2
                except:
                    next
                
            elif comparator=='Less than':
                try:
                    current_comparison = column1 < column2
                except:
                    next
                
            elif comparator=='Between':
                try:
                    current_comparison = column2 <= column1 and column1 <= column3 #Lower Value
                except:
                    next

            # Check if the previous row was not greater and the current row is greater
            if not prev_comparison and current_comparison:
                filtered_rows.append(row)
            
            # Update the previous comparison for the next iteration
            prev_comparison = current_comparison

        # Convert the filtered rows to a DataFrame
        filtered_database = pd.DataFrame(filtered_rows)

        sp500.append(filtered_database['Close'])
        ndx.append(filtered_database['Close'])
        rus2k.append(filtered_database['Close'])        

        return sp500, ndx, rus2k
    
    def generate_common_dates(self, intersection_dbs:list, selected_returninterval:int):
        appended_dates = [df.index for df in intersection_dbs]
        if appended_dates:
            unique_dates = reduce(lambda left,right: left.intersection(right), appended_dates).to_list()

            self.db['% Change Sel Interval'] = self.db['Close'].pct_change(selected_returninterval).shift(-selected_returninterval)

            self.common_dates = self.db[self.db.index.isin(unique_dates)]

            self.avg_return = self.common_dates['% Change Sel Interval'].mean()
            self.no_of_occurrences = len(self.common_dates['% Change Sel Interval'])
            self.no_of_positives = (self.common_dates['% Change Sel Interval'] > 0).sum()
            positive_percentage = self.no_of_positives/self.no_of_occurrences
            self.positive_percentage = '{:.2%}'.format(positive_percentage)