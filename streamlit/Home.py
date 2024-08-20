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
def streamdatatoinsights():
        fromdatatoinsights ='''This tool is used to figure out when in the S&P500, Nasdaq or Russell 2000 did X go up X% and Y was below price 40 (example).

        It utilizes the following:
        Python programming
        
        Skillsets working with large data from working with Power BI and other visualization tools,
        
        Statistical and financial background knowledge from my working knowledge in the industry
        
        Specific Python libraries and APIs: Pandas, numpy, Polars (moving towards Polars instead of Pandas), streamlit (what this app is hosted on), Yahoo 
        Finance's API, FRED (Federal Reserve Economic Data)'s API.
        
I call it What Transpired During Our Last Encounter [WTDOLLE](WTDOLLE).'''
        for word in fromdatatoinsights.split(" "):
                yield word + " "
                time.sleep(0.01)
st.write_stream(streamdatatoinsights)

