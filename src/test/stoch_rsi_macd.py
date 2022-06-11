import src.bot.strategy.smr as smr
from src.test.simulator.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import src.config as config



symbol = 'LUNCBUSD'
bot = Bot(symbol, BaseClient.KLINE_INTERVAL_3MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()


df = smr.analyze(df)

print(df.tail(30))
print("Back testing")
"""
    - Apply entry point with df 
    - Set stop loss + TP 
    - Calculatet profit 
"""

# ap= get_sub_plot_data(df)
# bot.viz(addplot=ap)