import src.bot.strategy.smr as smr
from src.test.simulator.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import src.config as config
from src.test.simulator.account import Account



symbol = 'WAVESUSDT'
account = Account(symbol)

bot = Bot(symbol, BaseClient.KLINE_INTERVAL_1HOUR, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()
df = smr.analyze(df)

last_price = 0
for index, row in df.iterrows():
    dftr = df.iloc[0:index]
    last_price = float(row['Close'])
    account.update_order(last_price, float(row['Close Time']) / 1000)
    if row['Buy']:  
        real = talib.ATR(dftr['High'], dftr['Low'], dftr['Close'], timeperiod=14)
        atr = real.iloc[-1]
        account.place_order(True, float(row['Close']), float(row['Close']) - 2 * atr,float(row['Close']) + 3 * atr, ctime=float(row['Close Time'])/ 1000)

    if row["Sell"]:
        real = talib.ATR(dftr['High'], dftr['Low'], dftr['Close'], timeperiod=14)
        atr = real.iloc[-1]
        account.place_order(False,float(row['Close']),  float(row['Close']) + 2 * atr,0.96 * float(row['Close']) - 3 * atr, ctime=float(row['Close Time'])/ 1000)
    
print(account.trading_data)
print(f"Balance: {account.get_actual_balance(last_price)}")
print(account.trading_infos)
ap= smr.get_sub_plot_data(df)
bot.viz(addplot=ap)