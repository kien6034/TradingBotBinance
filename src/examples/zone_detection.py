from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd


bot = Bot('BTCUSDT', BaseClient.KLINE_INTERVAL_3MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()

def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
  return support
def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
  return resistance

s =  np.mean(df['High'].astype(float) - df['Low'].astype(float))

def isFarFromLevel(l):
   return np.sum([abs(l-x) < s * 2  for x in levels]) == 0

real = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod = 14)


def get_ci(high, low, close, lookback):
    tr1 = pd.DataFrame(high - low).rename(columns = {0:'tr1'})
    tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns = {0:'tr2'})
    tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns = {0:'tr3'})
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').dropna().max(axis = 1)
    atr = tr.rolling(1).mean()
    highh = high.rolling(lookback).max()
    lowl = low.rolling(lookback).min()
    ci = 100 * np.log10((atr.rolling(lookback).sum()) / (highh - lowl)) / np.log10(lookback)
    return ci

ci = get_ci(df['High'].astype(float), df['Low'].astype(float), df['Close'].astype(float), 14)

plt.plot(ci.index, ci.values)
plt.axhline(38.2, linestyle = '--', linewidth = 1.5, color = 'grey')
plt.axhline(61.8, linestyle = '--', linewidth = 1.5, color = 'grey')
plt.show()
sys.exit()
levels = []
for i in range(2,df.shape[0]-2):
  if isSupport(df,i):
    l = float(df['Low'][i])
    if isFarFromLevel(l):
      levels.append(l)
  elif isResistance(df,i):
    l = float(df['High'][i])
    if isFarFromLevel(l):
      levels.append(l)

bot.viz(hlines=levels)

