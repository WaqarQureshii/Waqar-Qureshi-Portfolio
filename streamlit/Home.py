import streamlit as st

import time

# \\\\\\\\\\ TITLE /////////////
st.title("I'm a _Corporate Finance Leader_, that took a :blue[(very deep)] dive into _Software Engineering_")

#\\\\\\\\\\ HOW IT ALL BEGAN //////////////
def streamhowitbegan():
        howitbegan = "This website started as a passion project, born out of my fascination with both technology and finance. I wanted a place to house all my diverse projects and organize them for myself, ranging from Power BI development to Python programming. It currently showcases my python and statistical skillsets."
        howitbegan = "This website started as a passion project, born out of my fascination with both technology and finance. I wanted a place to house all my diverse projects and organize them for myself, ranging from Power BI development to Python programming. It currently showcases my python and statistical skillsets."
        
        for word in howitbegan.split(" "):
                yield word + " "
                time.sleep(0.01)
st.subheader("How It All Began")
st.write_stream(streamhowitbegan)

# \\\\\\\\\\ THE JOURNEY //////////
st.header(":blue[Project/s (adding these in every day)]")
with st.expander(label="WTDOLLE - What Transpired During Our Last Encounter 💹"):
        st.write('''This tool is used to answer questions such as: what's the historical record of when the S&P 500 went up 2% and the Yield Rate Difference between the US 10 year and 2 year was below 0''')
        python_tab, largedata_tab, stats_tab = st.tabs(["Python (Programming Language)", "Extracting & Transforming Large Data", "Statistical and Financial Knowledge"])

        with python_tab:
                st.subheader("🐍 Python Programming 🐍")
                st.write('''
        I used Python to:
        - Access 💲 Yahoo Finance's API 💲 to access historical data on the equity markets and volatility index
        - 🏛️ Access Federal Reserve Economic Data (FRED)'s 🏛️API to access US Federal Funds Rate as well as statistics such as Unemployment Rate and GDP.
        - Streamlit - used to interface the tool and gather input from the user to filter the multiple datasets based on the dates and parameters selected.
        - 🐼 Pandas 🐼 - an open source library for data analyhsis and manipulation: gathered user's input in order to manipulate the data, determine if paramters are met for an occurence, find the dates for the common occurences to feed into graphs and statistical data output.
        - 🐻‍❄️Polars🐻‍❄️ - multi-threaded query engine written in Rust - I am slowly moving my Pandas implementation to Polars to streamline data querying.
        ''')

        with largedata_tab:
                st.subheader("🏋️‍♂️ Large Data Transformation 🏋️‍♂️")
                st.write('''
        - 📈1 table = ~19,500 rows & ~95,000 points of data: Yahoo Finance's API can get daily data from 1950 for the S&P500 
        - ✖️ Multiply ✖️ this by, for example, 2, 8 or 16 tables for the various tables that can be queried: VIX (Volatility index), S&P 500, Nasdaq, Russell 2000, High-Yield Corporate Bonds (HYG), Equal-Weighted S&P 500 (RSP), US Market Debt (1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y) and US Federal Funds Rate
        - From the data extracted and metrics selected, I had to perform large data transformation to gather the relevant information for reporting. This requires working with the various data types (percent increases, dollar values and timevalues) in order to create 3 full charts that showcase where the user's inputs intersect on a graph.
                ''')

        with stats_tab:
                st.subheader("☕ Leveraging Working Experience ☕")
                st.write('''
        - 🎩 Transform the tables to include technical indicators requiring calculations such as Relative Strength Index (RSI), Moving Average (MA), % Changes.
        - Using my moderate industry and market knowledge, I designed and created user inputs based on useful metrics as well as many options that are available to the user.
                ''')

with st.expander(label="COMING SOON: REACT (Resume Enhancement and Customization Tool -GPT) 🤖"):
        st.write('''This app takes user inputs to ultimately output an action-oriented and job description-focused resume, but still keeping the original essence of the user's original resume submitted.''')
        python_tab2, gpt_tab = st.tabs(["Python (Programming Language)", "LangChain: Chat GPT Models"])

        with python_tab2:
                st.write('''
- Streamlit: a way to build and share apps - transform my Python scripts into an interactive web app that takes user input related to the job in question as well as the user's information such as their resume.                       
''')
