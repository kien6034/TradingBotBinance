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



symbol = 'LUNCBUSD'
account = Account(symbol)

bot = Bot(symbol, BaseClient.KLINE_INTERVAL_1MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()
df = smr.analyze(df)


for index, row in df.iterrows():
    dftr = df.iloc[0:index]
    if row['Buy']:  
        real = talib.ATR(dftr['High'], dftr['Low'], dftr['Close'], timeperiod=14)

        print(f"{index}: Buy ")

    if row["Sell"]:
        real = talib.ATR(dftr['High'], dftr['Low'], dftr['Close'], timeperiod=14)
        print(f"{index}: Sell")
    
    

    

sys.exit()
"""
    - Apply entry point with df 
    - Set stop loss + TP 
    - Calculatet profit 
"""

ap= smr.get_sub_plot_data(df)
bot.viz(addplot=ap)