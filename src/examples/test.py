from rsa import sign
from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpl


symbol = 'LINKUSDT'
bot = Bot('LINKUSDT', BaseClient.KLINE_INTERVAL_5MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()

df['Open Time'] = pd.to_datetime(df['Open Time']/1000, unit='s')
df['Close Time'] = pd.to_datetime(df['Close Time']/1000, unit='s')
numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)
df.index = df['Close Time']


buy = np.where((df['Close'] > df['Open']) & (df['Close'].shift(1) < df['Open'].shift(1)), 1, np.nan) * 0.95 * df['Low']

apd = mpl.make_addplot(buy,type='scatter')
mpl.plot(df,addplot=apd)
