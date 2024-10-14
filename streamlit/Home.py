import streamlit as st

import time

st.set_page_config(layout="wide")
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

with st.expander("WTDOLLE - What Transpired During Our Last Encounter"):
        st.write('''This tool is used to answer questions such as: what's the historical record of when the S&P 500 went up 2% and the Yield Rate Difference between the US 10 year and 2 year was below 0''')
        st.page_link("pages/1 - WTDOLLE - Stock Market Analysis.py", label="Project Link")
        python_tab, largedata_tab, stats_tab = st.tabs(["Python (Programming Language)", "Extracting & Transforming Large Data", "Statistical and Financial Knowledge"])

        with python_tab:
                st.subheader("🐍 Python Programming")
                st.write(
                        '''
        I used Python to:
        - Access 💲 Yahoo Finance's API 💲 to access historical data on the equity markets and volatility index
        - 🏛️ Access Federal Reserve Economic Data (FRED)'s 🏛️API to access US Federal Funds Rate as well as statistics such as Unemployment Rate and GDP.
        - Streamlit - used to interface the tool and gather input from the user to filter the multiple datasets based on the dates and parameters selected.
        - 🐼 Pandas 🐼 - an open source library for data analyhsis and manipulation: gathered user's input in order to manipulate the data, determine if paramters are met for an occurence, find the dates for the common occurences to feed into graphs and statistical data output.
        - 🐻‍❄️Polars🐻‍❄️ - multi-threaded query engine written in Rust - I am slowly moving my Pandas implementation to Polars to streamline data querying.
        '''
                )

        with largedata_tab:
                st.write(
                        '''
        - 📈1 table = ~19,500 rows & ~95,000 points of data: Yahoo Finance's API can get daily data from 1950 for the S&P500 
        - ✖️ Multiply ✖️ this by, for example, 2, 8 or 16 tables for the various tables that can be queried: VIX (Volatility index), S&P 500, Nasdaq, Russell 2000, High-Yield Corporate Bonds (HYG), Equal-Weighted S&P 500 (RSP), US Market Debt (1m, 3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y) and US Federal Funds Rate
        - From the data extracted and metrics selected, I had to perform large data transformation to gather the relevant information for reporting. This requires working with the various data types (percent increases, dollar values and timevalues) in order to create 3 full charts that showcase where the user's inputs intersect on a graph.
                '''
                )

        with stats_tab:
                st.write(
                        '''
        - 🎩 Transform the tables to include technical indicators requiring calculations such as Relative Strength Index (RSI), Moving Average (MA), % Changes.
        - Using my moderate industry and market knowledge, I designed and created user inputs based on useful metrics as well as many options that are available to the user.
                '''
                )

with st.expander("REACT: Resume Enhance and Customization Tool"):
        st.write('''REACT is pre-trained to be an action-oriented resume editor that takes your resume & your selected job description as a prompt. What differentiates this from other resume editors? It is action-oriented, maintains the spirit of your original resume, and incorporates the key job description skillsets that a hiring manager would look for.''')
        st.page_link("pages/2 - REACT - Resume Editor Tool.py", label="Project Link")
        python_tab, llm_tab, prompt_engineering_tab = st.tabs(["Python (Programming Language)", "Large Language Models", "Prompt Engineering"])

        with python_tab:
                st.subheader("🐍 Python Programming")
                st.write(
                        '''
        I used Python to:
        - Access Open AI's Large Language Model (LLM), chat-gpt's 4o model.
        - Streamlit - used to interface the tool and gather input from the user to prompt Open AI's LLM.
        '''
                )

        with llm_tab:
                st.subheader("📝 Using Large Language Models")
                st.write(
                        '''
        - Currently using ChatGPT's Large Language Model (LLM) that is built off strenuous AI and machine learning techniques.
        - Currently this method I have developed consumes a bit of Open AI tokens due to some prompt engineering required to get to a specific output (resume development).
        - In the future, I aim to train my own bot and contribute to the Hugging Face community.
                '''
                )

        with prompt_engineering_tab:
                st.subheader("👷 Prompt Engineering")
                st.write(
                        '''
        - 🎩 Because LLMs require an input or query to generate a response, there's a ton of engineering and guiding to the LLM in order to share the content of the output. The goal is to be as efficient as possible if you are using a third party paid LLM such as OpenAI.
        - The prompt engineering I used is to focus on creating a professional resume editor that incorporates the job description and the user's resume, to effectively create resume content that can pass the typical ATS.
                '''
                )