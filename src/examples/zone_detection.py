from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 


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