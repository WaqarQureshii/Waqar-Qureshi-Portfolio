import streamlit as st
import matplotlib.pyplot as plt

from functions.generate_databases import Generate_Equity, filter_indices

def apply_filters(input_start_date:str, input_end_date:str, input_interval:int, input_returninterval:int, equity_counter:int, debt_counter:int, filtered_db_lists:list, grammatical_selection:str="days"):
    # --- MAIN PAGE OF WTDOLLE - CHARTS AND PARAMETERS
        # -------------------- HEADER -------------------------
    st.header(f'WTDOLLE on {input_end_date}')

    # ---------MODIFYING THE METRIC FORMAT ------------------
    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 20px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    #--- PLOTTING GRAPH ---
    col1, col2, col3 = st.columns(3)
    graph1, graph2, graph3= st.columns(3)

    #-------INDICES PARAMETER SELECTION-------
    col1.subheader("S&P 500")
    col2.subheader("Nasdaq")
    col3.subheader("Russell 2000")
    
    return_days_list = [7,14,30,60,90,120,360]

    # --- Indices Generation ---
    if equity_counter+debt_counter > 0:
        #---S&P500 DATABASE GENERATION---
        if 'sp500' not in globals():
            sp500 = Generate_Equity()
            sp500.get_database(["^GSPC"], input_start_date, input_end_date, input_interval)
        
        if 'ndx' not in globals():
            ndx = Generate_Equity()
            ndx.get_database(["^IXIC"], input_start_date, input_end_date, input_interval)

        if 'rus2k' not in globals():
            rus2k = Generate_Equity()
            rus2k.get_database(["^RUT"], input_start_date, input_end_date, input_interval)
        

        #-------S&P500 GRAPH------

        fig,ax = plt.subplots()
        ax.set_title('S&P 500')
        ax.plot(sp500.lf.select("Date").collect(), sp500.lf.select("Close").collect(), linewidth=0.5, color="black")

        sp500_filtered_lf, sp500_return_stats = filter_indices(filtered_db_lists, sp500.lf, input_returninterval, return_days_list, grammatical_selection)

        try:
            ax.scatter(sp500_filtered_lf.select("Date").collect(), sp500_filtered_lf.select("Close").collect(), marker='.', color='red', s =10)
        except AttributeError:
            graph1.write("There are no scenarios that exist like this.")

        graph1.pyplot(fig)

        graph1.dataframe(sp500_return_stats.collect(), hide_index=True)

    #     #---NASDAQ DATABASE GENERATION---
        fig,ax = plt.subplots()
        ax.set_title('Nasdaq')
        ax.plot(ndx.lf.select("Date").collect(), ndx.lf.select("Close").collect(), linewidth=0.5, color="black")

        ndx_filtered_lf, ndx_return_stats = filter_indices(filtered_db_lists, ndx.lf, input_returninterval, return_days_list, grammatical_selection)

        try:
            ax.scatter(ndx_filtered_lf.select("Date").collect(), ndx_filtered_lf.select("Close").collect(), marker='.', color='red', s =10)
        except AttributeError:
            graph2.write("There are no scenarios that exist like this.")

        graph2.pyplot(fig)

        graph2.dataframe(ndx_return_stats.collect(), hide_index=True)
            
#     #---Russell 2000 DATABASE GENERATION---
        fig,ax = plt.subplots()
        ax.set_title('Russell 2000')
        ax.plot(rus2k.lf.select("Date").collect(), rus2k.lf.select("Close").collect(), linewidth=0.5, color="black")

        rus2k_filtered_lf, rus2k_return_stats = filter_indices(filtered_db_lists, rus2k.lf, input_returninterval, return_days_list, grammatical_selection)

        try:
            ax.scatter(rus2k_filtered_lf.select("Date").collect(), rus2k_filtered_lf.select("Close").collect(), marker='.', color='red', s =10)
        except AttributeError:
            graph3.write("There are no scenarios that exist like this.")

        graph3.pyplot(fig)

        graph3.dataframe(rus2k_return_stats.collect(), hide_index=True)