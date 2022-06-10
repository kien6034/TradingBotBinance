from ..bot.strategy.stoch_macd_rsi import get_sub_plot_data, analyze
from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd


symbol = 'LUNCBUSD'
bot = Bot(symbol, BaseClient.KLINE_INTERVAL_3MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()


df = analyze(df)
ap= get_sub_plot_data(df)

bot.viz(addplot=ap)