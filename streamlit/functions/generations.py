import yfinance as yf
import pandas_ta as ta
import pandas as pd

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
        self.db['Ratio']=self.db[f'{numerator} Close']/self.db[f'{denominator} Close']
        self.db['Ratio % Chg']=(self.db['Ratio'].pct_change()*100).round(2)
        
        #Create rsi and ma columns
        self.db['rsi'] = ta.rsi(close = self.db['Ratio'], length=rsi_length)
        self.db['ma'] = ta.sma(close = self.db['Ratio'], length=ma_length)

        #Creating variables for UI
        self.curr_rsi = self.db['rsi'].iloc[-1]
        self.curr_ma = int(self.db['ma'].iloc[-1])
        self.curr_p = self.db['Ratio'].iloc[-1]
        self.pctchg_int = self.db['Ratio % Chg'].iloc[-1]
        self.pctchg_str = "{:.2%}".format(self.pctchg_int / 100)

    def metric_vs_selection(self, comparison_type:str, comparator:str, selected_value, sp500:pd.DataFrame, ndx:pd.DataFrame, rus2k:pd.DataFrame):
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

        sp500.append(filtered_database)
        ndx.append(filtered_database)
        rus2k.append(filtered_database)        

        return sp500, ndx, rus2k

    
class Generate_Yield():
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
