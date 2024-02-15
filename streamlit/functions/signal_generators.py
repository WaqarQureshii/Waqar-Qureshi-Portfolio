import streamlit as st

from functools import reduce

@st.cache_data
def signal_pct_change_auto(database, pct_change_floor, pct_change_ceil, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    filtered_database = database[(database['% Change'] >= pct_change_floor) & (database['% Change'] <= pct_change_ceil)]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_pct_change_manual(database, comparator, selected_value, current_value, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    if comparator == 'Greater than':
        boolean = current_value*100 >= selected_value
        
        filtered_database = database[database['% Change'] >= selected_value/100]
        sp500_intersection.append(filtered_database)
        nasdaq_intersection.append(filtered_database)
        rus2k_intersection.append(filtered_database)
    else:
        boolean = current_value*100 <= selected_value
        
        filtered_database = database[database['% Change'] <= selected_value/100]
        sp500_intersection.append(filtered_database)
        nasdaq_intersection.append(filtered_database)
        rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_level_greater_than(current_value, comparator_value_selected, database, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = current_value >= comparator_value_selected
    filtered_database = database[database['Close'] >= comparator_value_selected]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_level_lower_than(level_selected, comparator_value_selected, database, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = level_selected <= comparator_value_selected
    filtered_database = database[database['Close'] <= comparator_value_selected]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_p_greater_than_MA(database, price, ma, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = price > ma
    filtered_database = database[database['Close'] > database['ma']]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)
    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_p_lower_than_MA(database, price, ma, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = price < ma
    filtered_database = database[database['Close'] < database['ma']]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)
    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_rsi_greater_than(database, rsi_current, rsi_selected_value, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = rsi_current > rsi_selected_value
    
    filtered_database = database[database['rsi'] > rsi_selected_value]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)
    
    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_rsi_lower_than(database, rsi_current, rsi_selected_value, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = rsi_current < rsi_selected_value
    
    filtered_database = database[database['rsi'] < rsi_selected_value]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)
    
    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def yieldcurve_diff_greater(database, current_difference, selected_difference, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = current_difference >= selected_difference
    filtered_database = database[database['Yield Diff'] >= selected_difference]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def yieldcurve_diff_lower(database, current_difference, selected_difference, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = current_difference <= selected_difference
    filtered_database = database[database['Yield Diff'] <= selected_difference]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_ratio_value(database, comparator, curr_ratio, selected_level ,sp500_intersection, nasdaq_intersection, rus2k_intersection):
    if comparator == 'Greater than':
        boolean = curr_ratio >= selected_level
        filtered_database = database[database['Ratio'] >= selected_level]
    elif comparator == 'Lower than':
        boolean = curr_ratio <= selected_level
        filtered_database = database[database['Ratio'] <= selected_level]
    
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_ratio_pct_value(database, comparator, ratio_pct_curr, selected_level ,sp500_intersection, nasdaq_intersection, rus2k_intersection):
    if comparator == 'Greater than':
        boolean = ratio_pct_curr >= selected_level
        filtered_database = database[database['Ratio % Chg'] >= selected_level]
    elif comparator == 'Lower than':
        boolean = ratio_pct_curr <= selected_level
        filtered_database = database[database['Ratio % Chg'] <= selected_level]
    
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_pct_positive(db, db_intersection, selected_return_interval):
    appended_dates = [df.index for df in db_intersection] #collect all of the dates from the signals created
    if appended_dates:
        unique_dates = reduce(lambda left, right: left.intersection(right), appended_dates).to_list()

        db['% Change Sel Interval'] = db['Close'].pct_change(selected_return_interval).shift(-selected_return_interval) #calculate future return based on selected return interval

        db_filtered_dates = db[db.index.isin(unique_dates)] #filter database for only the dates that are in common - this is in order to plot red dots on the graphs

        avg_db_return = db_filtered_dates['% Change Sel Interval'].mean()
        no_of_occurrences = len(db_filtered_dates['% Change Sel Interval'])
        no_of_positives = (db_filtered_dates['% Change Sel Interval'] > 0).sum()
        positive_percentage = no_of_positives/no_of_occurrences
        positive_percentage = '{:.2%}'.format(positive_percentage)

        return db_filtered_dates, avg_db_return, no_of_occurrences, positive_percentage

    else:
        pass
