import yfinance as yf
import pandas_ta as ta
import pandas as pd

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
