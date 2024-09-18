import streamlit as st

import time

# \\\\\\\\\\ TITLE /////////////
st.title("I'm a _Corporate Finance Leader_, that took a :blue[(very deep)] dive into _Software Engineering_")

#\\\\\\\\\\ HOW IT ALL BEGAN //////////////
def streamhowitbegan():
        howitbegan = "This website started as a passion project, born out of my fascination with both technology and finance. I wanted a place to house all my diverse projects and organize them for myself, ranging from Power BI development to Python programming. It currently showcases my python and statistical skillsets."
        
        for word in howitbegan.split(" "):
                yield word + " "
                time.sleep(0.01)
st.subheader("How It All Began")
st.write_stream(streamhowitbegan)

# \\\\\\\\\\ THE JOURNEY //////////
st.header(":blue[Project/s (adding these in every day)]")
st.subheader("WTDOLLE - What Transpired During Our Last Encounter")
st.write('''This tool is used to answer questions such as: what's the historical record of when the S&P 500 went up 2% and the Yield Rate Difference between the US 10 year and 2 year was below 0''')
python_tab, largedata_tab, stats_tab = st.tabs(["Python (Programming Language)", "Extracting & Transforming Large Data", "Statistical and Financial Knowledge"])

def streampython():
        python_information='''
I used Python to:
- Access 💲 Yahoo Finance's API 💲 to access historical data on the equity markets and volatility index
- 🏛️ Access Federal Reserve Economic Data (FRED)'s 🏛️API to access US Federal Funds Rate as well as statistics such as Unemployment Rate and GDP.
- Streamlit - used to interface the tool and gather input from the user to filter the multiple datasets based on the dates and parameters selected.
- 🐼 Pandas 🐼 - an open source library for data analyhsis and manipulation: gathered user's input in order to manipulate the data, determine if paramters are met for an occurence, find the dates for the common occurences to feed into graphs and statistical data output.
- 🐻‍❄️Polars🐻‍❄️ - multi-threaded query engine written in Rust - I am slowly moving my Pandas implementation to Polars to streamline data querying.
'''
        for word in python_information.split(" "):
                yield word + " "
                time.sleep(0.01)

def streamlargedata():
        largedata_info='''
- 📈1 table = ~19,500 rows & ~95,000 points of data: Yahoo Finance's API can get daily data from 1950 for the S&P500 
- ✖️ Multiply ✖️ this by, for example, 2, 8 or 16 tables for the various tables that can be queried: VIX (Volatility index), S&P 500, Nasdaq, Russell 2000, High-Yield Corporate Bonds (HYG), Equal-Weighted S&P 500 (RSP), US Market Debt (1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y) and US Federal Funds Rate
- From the data extracted and metrics selected, I had to perform large data transformation to gather the relevant information for reporting. This requires working with the various data types (percent increases, dollar values and timevalues) in order to create 3 full charts that showcase where the user's inputs intersect on a graph.
        '''
        for word in largedata_info.split(" "):
                yield word + " "
                time.sleep(0.01)

def stream_stats():
        stats_info='''
- 🎩 Transform the tables to include technical indicators requiring calculations such as Relative Strength Index (RSI), Moving Average (MA), % Changes.
- Using my moderate industry and market knowledge, I designed and created user inputs based on useful metrics as well as many options that are available to the user.
        '''
        for word in stats_info.split(" "):
                yield word + " "
                time.sleep(0.01)

with python_tab:
        st.subheader("🐍 Python Programming")
        st.write_stream(streampython)

with largedata_tab:
        st.write_stream(streamlargedata)

with stats_tab:
        st.write_stream(stream_stats)

# def streamdatatoinsights():
#         fromdatatoinsights ='''This tool is used to figure out when in the S&P500, Nasdaq or Russell 2000 did X go up X% and Y was below price 40 (example).

#         It utilizes the following:
#         🐍 Python programming
        
#         📉 Skillsets working with large data from working with Power BI and other visualization tools,
        
#         🎲 Statistical and financial background knowledge from my working knowledge in the industry
        
#         Specific Python libraries and APIs: Pandas, numpy, Polars (moving towards Polars instead of Pandas), streamlit (what this app is hosted on), Yahoo 
#         Finance's API, FRED (Federal Reserve Economic Data)'s API.
        
# I call it What Transpired During Our Last Encounter [WTDOLLE: Stock Market Analysis - see sidebar].'''
#         for word in fromdatatoinsights.split(" "):
#                 yield word + " "
#                 time.sleep(0.01)
# st.write_stream(streamdatatoinsights)

