import streamlit as st

@st.cache_data
def signal_pct_change_auto(database, pct_change_floor, pct_change_ceil, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    filtered_database = database[(database['% Change'] >= pct_change_floor) & (database['% Change'] <= pct_change_ceil)]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return sp500_intersection, nasdaq_intersection, rus2k_intersection

@st.cache_data
def signal_level_greater_than(level_selected, comparator_value_selected, database, sp500_intersection, nasdaq_intersection, rus2k_intersection):
    boolean = level_selected >= comparator_value_selected
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
    boolean = current_difference >= selected_difference
    filtered_database = database[database['Yield Diff'] <= selected_difference]
    sp500_intersection.append(filtered_database)
    nasdaq_intersection.append(filtered_database)
    rus2k_intersection.append(filtered_database)

    return boolean, sp500_intersection, nasdaq_intersection, rus2k_intersection