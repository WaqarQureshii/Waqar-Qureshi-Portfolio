import streamlit as st

import time

# \\\\\\\\\\ TITLE /////////////
st.title("I'm a _Corporate Finance Leader_, that took a :blue[(very deep)] dive into _Software Engineering_")

#\\\\\\\\\\ HOW IT ALL BEGAN //////////////
def streamhowitbegan():
        howitbegan = "This website started as a passion project, born out of my fascination with both technology and finance. I wanted a place to house all my diverse projects and organize them (for myself), ranging from Power BI development to Python programming. Little did I know that this humble beginning would evolve into what you see today."
        
        for word in howitbegan.split(" "):
                yield word + " "
                time.sleep(0.01)
st.subheader("How It All Began")
st.write_stream(streamhowitbegan)

# \\\\\\\\\\ THE JOURNEY //////////
st.header(":blue[The Journey]")
st.subheader("From Data to Insights")
def streamdatatoinsights():
        fromdatatoinsights ="One of my favorite creations is a custom stock market analyzer. It all began with questions I often asked: “What happened the last time a particular metric went up 2% while yields went down 1%?” I was curious about the statistical chances of a stock price increase over different time frames—1 week, 1 month, and 1 year. I nicknamed it [WTDOLLE](WTDOLLE)."
        for word in fromdatatoinsights.split(" "):
                yield word + " "
                time.sleep(0.01)
st.write_stream(streamdatatoinsights)

st.subheader("Creative Python Development")
def streamcreativepydev():
        creativepydev = '''
        Armed with Python and a passion for data, I delved into historical stock data, economic indicators, and market trends. The result? A powerful tool that provides insights into stock behavior based on specific conditions. Whether you're an investor, trader, or simply curious about the markets, this analyzer can help you make informed decisions.
        '''
        for word in creativepydev.split(" "):
                yield word + " "
                time.sleep(0.01)
st.write_stream(streamcreativepydev)