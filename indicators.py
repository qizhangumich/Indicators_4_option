# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 23:50:11 2021

@author: ZhangQi
"""
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import streamlit as st

#source = pd.read_csv("china_concept.csv",encoding="GB2312")
#tickers = list(source.Ticker2)
#names = list(source.Name)


import requests
import os
import sys
# check if the library folder already exists, to avoid building everytime you load the pahe
if not os.path.isdir("/tmp/ta-lib"):

    # Download ta-lib to disk
    with open("/tmp/ta-lib-0.4.0-src.tar.gz", "wb") as file:
        response = requests.get(
            "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
        )
        file.write(response.content)
    # get our current dir, to configure it back again. Just house keeping
    default_cwd = os.getcwd()
    os.chdir("/tmp")
    # untar
    os.system("tar -zxvf ta-lib-0.4.0-src.tar.gz")
    os.chdir("/tmp/ta-lib")
    # build
    os.system("./configure --prefix=/home/appuser")
    os.system("make")
    # install
    os.system("make install")
    # install python package
    os.system(
        'pip3 install --global-option=build_ext --global-option="-L/home/appuser/lib/" --global-option="-I/home/appuser/include/" ta-lib'
    )
    # back to the cwd
    os.chdir(default_cwd)
    print(os.getcwd())
    sys.stdout.flush()

# add the library to our current environment
from ctypes import *

lib = CDLL("/home/appuser/lib/libta_lib.so.0")
# import library


import talib as ta

tickers = ["BEST","RLX","EDU","1810.HK","WDH","CAAS","VZ","DIS","KO","MOMO","PYPL","AAPL","TSLA","NVDA","FB"]
names =["百世","雾芯","新东方","小米","水滴","汽车系统","Verizon","迪士尼","可乐","陌陌","Paypal","苹果","特斯拉","英伟达","脸书"]


ticker = st.sidebar.selectbox(
    '股票代码：',
     tickers)

name = names[tickers.index(ticker)]

st.title(name)


start = dt.datetime(2021, 1, 1) 
end = dt.date.today()



stock = yf.Ticker(ticker)
period = 20
df= stock.history(ticker, start=start, end=end)

up,mid,low = ta.BBANDS(df.Close,timeperiod=period,nbdevup=2,nbdevdn=2,matype=0)

ema = ta.EMA(df.Close,timeperiod=period)

rsi = ta.RSI(df.Close,timeperiod=period)

macd,msig,mhist = ta.MACD(df.Close,fastperiod=5,slowperiod=20,signalperiod=5)
#MACD and average series are customarily displayed as continuous lines in a plot whose horizontal axis is time, whereas the divergence is shown as a bar graph (often called a histogram).
# These three series are: the MACD series proper, the "signal" or "average" series, and the "divergence" series which is the difference between the two. The MACD series is the difference between a "fast" (short period) exponential moving average (EMA), and a "slow" (longer period) EMA of the price series. The average series is an EMA of the MACD series itself.
#A "signal-line crossover" occurs when the MACD and average lines cross; that is, when the divergence (the bar graph) changes sign. The standard interpretation of such an event is a recommendation to buy if the MACD line crosses up through the average line (a "bullish" crossover), or to sell if it crosses down through the average line (a "bearish" crossover).[6] These events are taken as indications that the trend in the stock is about to accelerate in the direction of the crossover.
#A "zero crossover" event occurs when the MACD series changes sign, that is, the MACD line crosses the horizontal zero axis. This happens when there is no difference between the fast and slow EMAs of the price series. A change from positive to negative MACD is interpreted as "bearish", and from negative to positive as "bullish". Zero crossovers provide evidence of a change in the direction of a trend but less confirmation of its momentum than a signal line crossover.
#false signals:A prudent strategy may be to apply a filter to signal line crossovers to ensure that they have held up. An example of a price filter would be to buy if the MACD line breaks above the signal line and then remains above it for three days. 

obv = ta.OBV(df.Close,df.Volume)
mfi = ta.MFI(df.High,df.Low,df.Close,df.Volume,timeperiod=10)

df["Up"] = up
df["Low"] = low
df["Mid"] = mid
df["EMA"] = ema
df["RSI"] = rsi
df["MACD"] = macd
df["MACD_signal"] = msig
df["MACD_diverge"] = mhist
df["OBV"] = obv
df["MFI"]=mfi

fig, (ax0,ax1,ax2,ax3,ax4,ax5) = plt.subplots(nrows=6)
#fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
#https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
#fig.tight_layout()
fig.set_size_inches(20, 30)

ax0.plot(df.Close,label="close",linewidth=2,color="black")
ax0.plot(df.Up,label="up boundary")
ax0.plot(df.Low,label="low boundary")
ax0.plot(df.Mid,label="mid",linestyle=":")
ax0.fill_between(df.Up.index,df.Up,df.Low,facecolor='gray',alpha=0.1)
ax0.set_title('Bolling Band')
#ax0.tick_params(axis='x',rotation=30) 
ax0.legend(loc='upper right')

ax1.plot(df.Close,label="close")
ax1.plot(df.EMA,label="EMA",linewidth=2,color="black")
ax1.set_title('EMA')
#ax1.tick_params(axis='x',rotation=30) 
ax1.legend(loc='upper right')

ax2.plot(df.RSI,label="RSI")
ax2.axhline(y=70, color='r', linestyle='-')
ax2.axhline(y=30, color='g', linestyle='-')
ax2.set_title('RSI')
#ax2.tick_params(axis='x',rotation=30) 
ax2.legend(loc='upper right')

ax3.plot(df.MACD,label="MACD",linewidth=2)
ax3.plot(df.MACD_signal,label="MACD_signal")
clrs = ['red' if x < 0 else 'green' for x in df.MACD_diverge.values ]
ax3.bar(df.MACD_diverge.index,df.MACD_diverge,color=clrs)
ax3.set_title('MACD')
#ax3.tick_params(axis='x',rotation=45)
ax3.legend(loc='upper right')


ax4.plot(df.OBV,label="OBV",linewidth=2)
ax4.set_title('OBV')
#ax3.tick_params(axis='x',rotation=45)
ax4.legend(loc='upper right')

ax5.plot(df.MFI,label="MFI")
ax5.axhline(y=80, color='r', linestyle='-')
ax5.axhline(y=20, color='g', linestyle='-')
ax5.set_title('MFI')
#ax2.tick_params(axis='x',rotation=30) 
ax5.legend(loc='upper right')


st.pyplot(fig)

info = stock.info
indicators = ['marketCap','trailingPE','priceToSalesTrailing12Months','totalRevenue','revenuePerShare','revenueGrowth','returnOnEquity',"grossMargins","profitMargins"]

col1, col2, col3 = st.columns(3)
col1.metric(indicators[0], "{:,.2f}".format(info[indicators[0]]/100000000))
try:
    col2.metric(indicators[1], "{:,.2f}".format(info[indicators[1]]))
except:
    col2.metric(indicators[1], "NA")
col3.metric(indicators[2], "{:,.2f}".format(info[indicators[2]]))

col4, col5, col6 = st.columns(3)
col4.metric(indicators[3], "{:,.2f}".format(info[indicators[3]]/100000000))
col5.metric(indicators[4], "{:,.2f}".format(info[indicators[4]]))
col6.metric(indicators[5], "{:,.2f}".format(info[indicators[5]]))

col7, col8, col9 = st.columns(3)
col7.metric(indicators[6], "{:,.2f}".format(info[indicators[6]]))
col8.metric(indicators[7], "{:,.2f}".format(info[indicators[7]]))
col9.metric(indicators[8], "{:,.2f}".format(info[indicators[8]]))
