from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf


symbol = 'LUNABUSD'
bot = Bot(symbol, BaseClient.KLINE_INTERVAL_1MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()

slowk, slowd = talib.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=1, slowd_period=3)
rsi = real = talib.RSI(df['Close'], timeperiod=14)
macd, macdsignal, macdhist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

df["%K"] = slowk
df["%D"] = slowd 
df["rsi"] = rsi
df["macd"] = macdhist

df.dropna(inplace=True)

# Lagging
def gettriggers(df, lags, buy=True):
    df2 = pd.DataFrame()
   
    if buy:
        # Pandas.shift: 
        mask= (df['%K']< 25) & (df['%D'] < 25)
    else: 
        mask= (df['%K'] > 75) & (df['%D'] > 75)

    df2 = pd.concat([df2, mask])

    return df2.rolling(lags).sum()

df['Buytrigger'] = np.where(gettriggers(df, 3),1,0) # if we get a buy signal (sum is larger than 0) we get a 1, if we dont we get a 0.
df['Selltrigger'] = np.where(gettriggers(df,3, False),1,0)
df['Buy'] = np.where((df.Buytrigger)  & (df.macd > 0) & (df.rsi > 50),1,0)
df['Sell'] = np.where((df.Selltrigger) & (df.macd < 0) & (df.rsi < 50),1,0)

Buying_dates, Selling_dates = [], []

for i in range(len(df) - 1): 
    if df.Buy.iloc[i]: # checking if each row has a buy signal
        Buying_dates.append(df.iloc[i +1].name) # if condition is met, you buy at the next timepoint (next row)
        for num,j in enumerate(df.Sell[i:]): # checking from the buying date if the selling conditions are fulfilled.
            if j: # j is the signal if its 1 or 0 
                Selling_dates.append(df.iloc[i + num + 1].name) # i + num because num is the number of iterations.
                break


buy = np.where((df['Buy'] == 1), 1, np.nan) * 1 * df['Low'].astype(float)
sell = np.where((df['Sell'] == 1), 1, np.nan) * 1 * df['High'].astype(float)

ap = []
if not buy.isnull().all():
    ap.append(mpf.make_addplot(buy, type='scatter', marker='^', markersize=100, color='g'))

if not sell.isnull().all():
    ap.append(mpf.make_addplot(sell, type='scatter', marker='v', markersize=100, color='r'))

bot.viz(df, addplot=ap)