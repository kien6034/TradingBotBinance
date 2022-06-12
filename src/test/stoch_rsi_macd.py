import src.bot.strategy.smr as smr
from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import src.config as config
from src.simulator.account import Account


symbol = 'LINKUSDT'
account = Account(symbol)

bot = Bot(symbol, BaseClient.KLINE_INTERVAL_15MINUTE, BaseClient.KLINE_INTERVAL_5MINUTE)
df= bot.get_historical_datas()
df = smr.analyze(df)


last_price = 0
for index, row in df.iterrows():
    dftr = df.iloc[0:index]
    last_price = float(row['Close'])
    account.update_order(last_price, float(row['Close Time']) / 1000)
    close = float(row['Close'])
    ctime=float(row['Close Time'])/ 1000
    real = talib.ATR(dftr['High'], dftr['Low'], dftr['Close'], timeperiod=14)
    atr = real.iloc[-1]

    nan = float("nan")
    if account.on_trading > 0 and row['Selltrigger']: # buying
        account.place_order(False, close,  nan,nan, ctime)   

    if account.on_trading < 0 and row['Buytrigger']: # selling
        account.place_order(True, close, nan,nan, ctime)   
 

    if row['Buy']:  
        account.place_order(True, close, close - 4 * atr,nan, ctime)

    if row["Sell"]:
        account.place_order(False,close, close + 4 * atr,nan, ctime)
    
print(account.trading_data)
print(f"Balance: {account.get_actual_balance(last_price)}")
print(account.trading_infos)
ap= smr.get_sub_plot_data(df)
bot.viz(addplot=ap)