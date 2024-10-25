import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import polars as pl
import numpy as np

from functions.generate_databases import Generate_Equity, filter_indices

def apply_filters(input_start_date:str, input_end_date:str, input_interval:int, input_returninterval:int, equity_counter:int, debt_counter:int, econ_stat_counter:int, filtered_db_lists:list, grammatical_selection:str="days"):
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
    
    return_days_list = [5,10,22,50,200]

    # --- Indices Generation ---
    if (equity_counter+debt_counter+econ_stat_counter) > 0:
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
        
        if 'hsi' not in globals():
            hsi = Generate_Equity()
            hsi.get_database(["HSI"], input_start_date, input_end_date, input_interval)
        

        #-------S&P500 GRAPH------
        sp500_filtered_lf, sp500_return_stats = filter_indices(filtered_db_lists, sp500.lf, input_returninterval, return_days_list, grammatical_selection)

        linefig = px.line(data_frame=sp500.lf.select(["Date", "Close"]).collect(),
                      x="Date",
                      y="Close")
        scatterfig = px.scatter(sp500_filtered_lf.select(["Date", "Close"]).collect(),
                      "Date",
                      "Close")
        fig = go.Figure(data=linefig.data+scatterfig.data)
        fig.update_traces(line=dict(width=1.0),
                          marker=dict(size=7,
                                    color="red",
                                    opacity=1))

        graph1.plotly_chart(fig, use_container_width=True)

        graph1.dataframe(sp500_return_stats.collect(), hide_index=True)



    #     #---NASDAQ DATABASE GENERATION---
        ndx_filtered_lf, ndx_return_stats = filter_indices(filtered_db_lists, ndx.lf, input_returninterval, return_days_list, grammatical_selection)

        linefig = px.line(data_frame=ndx.lf.select(["Date", "Close"]).collect(),
                      x="Date",
                      y="Close")
        scatterfig = px.scatter(ndx_filtered_lf.select(["Date", "Close"]).collect(),
                      "Date",
                      "Close")
        fig = go.Figure(data=linefig.data+scatterfig.data)
        fig.update_traces(line=dict(width=1),
                          marker=dict(size=7,
                                    color="red",
                                    opacity=1))

        graph2.plotly_chart(fig, use_container_width=True)

        graph2.dataframe(ndx_return_stats.collect(), hide_index=True)
            
#     #---Russell 2000 DATABASE GENERATION---
        rus2k_filtered_lf, rus2k_return_stats = filter_indices(filtered_db_lists, rus2k.lf, input_returninterval, return_days_list, grammatical_selection)

        linefig = px.line(data_frame=rus2k.lf.select(["Date", "Close"]).collect(),
                      x="Date",
                      y="Close")
        scatterfig = px.scatter(rus2k_filtered_lf.select(["Date", "Close"]).collect(),
                      "Date",
                      "Close")
        fig = go.Figure(data=linefig.data+scatterfig.data)
        fig.update_traces(line=dict(width=1),
                          marker=dict(size=7,
                                    color="red",
                                    opacity=1))

        graph3.plotly_chart(fig, use_container_width=True)

        graph3.dataframe(rus2k_return_stats.collect(), hide_index=True)



        #------HISTOGRAMS
        sp500_array = sp500_filtered_lf.select("Return Stats").drop_nulls().collect().to_series().to_list()
        ndx_array = ndx_filtered_lf.select("Return Stats").drop_nulls().collect().to_series().to_list()
        rus2k_array = rus2k_filtered_lf.select("Return Stats").drop_nulls().collect().to_series().to_list()

        histogram_data = [sp500_array, ndx_array, rus2k_array]
        group_labels=["SP500", 'Nasdaq', 'Russell 2000']

        hist_fig = ff.create_distplot(histogram_data, group_labels, curve_type="normal")

        st.plotly_chart(hist_fig)
        
# #     #---Han Seng Index DATABASE GENERATION---
#         rowcol1.subheader("Han Seng Index (HSI)")
#         hsi_filtered_lf, hsi_return_stats = filter_indices(filtered_db_lists, hsi.lf, input_returninterval, return_days_list, grammatical_selection)

#         linefig = px.line(data_frame=hsi.lf.select(["Date", "Close"]).collect(),
#                       x="Date",
#                       y="Close")
#         scatterfig = px.scatter(hsi_filtered_lf.select(["Date", "Close"]).collect(),
#                       "Date",
#                       "Close")
#         fig = go.Figure(data=linefig.data+scatterfig.data)
#         fig.update_traces(line=dict(width=1),
#                           marker=dict(size=7,
#                                     color="red",
#                                     opacity=1))

#         rowcol1.plotly_chart(fig, use_container_width=True)

#         rowcol1.dataframe(hsi_return_stats.collect(), hide_index=True)
