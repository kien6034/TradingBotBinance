from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd


bot = Bot('BTCUSDT', BaseClient.KLINE_INTERVAL_5MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()


macd, macdsignal, macdhist =  talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

plt.plot(macd.index, macd.values)
plt.plot(macdsignal.index, macdsignal.values)
plt.show()

print(macd)
print(macdsignal)
print(macdhist)