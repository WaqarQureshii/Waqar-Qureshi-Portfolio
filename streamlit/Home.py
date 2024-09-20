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
        st.write('''This tool helps answer questions like: *What’s the historical record when the S&P 500 rose 2% and the yield curve between the US 10-year and 2-year bonds was inverted (below 0)?*''')
        python_tab, largedata_tab, stats_tab = st.tabs(["Python (Programming Language)", "Extracting & Transforming Large Data", "Statistical and Financial Knowledge"])

        with python_tab:
                st.subheader("🐍 Python Programming 🐍")
                st.write('''
        I used Python for:
        - Yahoo Finance API 💲: Accessed historical data on equity markets and the volatility index (VIX
        - Federal Reserve Economic Data (FRED) API 🏛️: Retrieved US Federal Funds Rate data, along with other economic statistics such as the Unemployment Rate and GDP.
        - Streamlit: Developed a user-friendly interface allowing users to filter multiple datasets based on dates and selected parameters.
        - Pandas 🐼: Leveraged this open-source library for data analysis and manipulation. It processes user inputs, manipulates data to check whether conditions are met, identifies relevant dates, and generates corresponding charts and statistical outputs.
        - Polars 🐻‍❄️: Currently transitioning from Pandas to Polars—a fast, multi-threaded query engine written in Rust—to optimize data querying.
        ''')

        with largedata_tab:
                st.subheader("🏋️‍♂️ Large Data Transformation 🏋️‍♂️")
                st.write('''
        - Dataset Size: Each table consists of around 19,500 rows and 95,000 data points. Yahoo Finance’s API provides daily data on the S&P 500 from the year 1950.
        - Scaling Up: Multiply that by 2, 8, or 16 tables depending on the query, which may include various datasets like the VIX, S&P 500, Nasdaq, Russell 2000, High-Yield Corporate Bonds (HYG), Equal-Weighted S&P 500 (RSP), US Treasury Debt (1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y), and the US Federal Funds Rate.
        - Data Transformation: I handled complex data transformations to generate meaningful insights and reports. This involved working with various data types (percentage changes, dollar values, time series) to create three comprehensive charts that illustrate where the user’s selected parameters intersect.
                ''')

        with stats_tab:
                st.subheader("☕ Leveraging Working Experience ☕")
                st.write('''
        - 🎩 Technical Indicators: I implemented calculations for technical indicators such as the Relative Strength Index (RSI), Moving Averages (MA), and percentage changes within the datasets.
        - User-Driven Design: Using my experience in the financial markets, I created input options based on relevant metrics, ensuring users have a wide array of useful parameters to choose from.
                ''')

with st.expander(label="COMING SOON: REACT (Resume Enhancement and Customization Tool -GPT) 🤖"):
        st.write('''This app takes user inputs to ultimately output an action-oriented and job description-focused resume, but still keeping the original essence of the user's original resume submitted.''')
        python_tab2, gpt_tab = st.tabs(["Python (Programming Language)", "LangChain: Chat GPT Models"])

        with python_tab2:
                st.write('''
- Streamlit: a way to build and share apps - transform my Python scripts into an interactive web app that takes user input related to the job in question as well as the user's information such as their resume.                       
''')
