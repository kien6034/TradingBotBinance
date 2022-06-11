import talib
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf
from ...config import STOCH_HIGH, STOCH_LOW, LAG



def process_df(df):
    slowk, slowd = talib.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=1, slowd_period=3)
    rsi = talib.RSI(df['Close'], timeperiod=14)
    _, _, macdhist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

    df["%K"] = slowk
    df["%D"] = slowd 
    df["rsi"] = rsi
    df["macd"] = macdhist
    df.dropna(inplace=True)
    return df



# Lagging
def gettriggers(df, buy=True):
    df2 = pd.DataFrame()
   
    if buy:
        # Pandas.shift: 
        mask= (df['%K']< STOCH_LOW) & (df['%D'] < STOCH_LOW)
    else: 
        mask= (df['%K'] > STOCH_HIGH) & (df['%D'] > STOCH_HIGH)

    df2 = pd.concat([df2, mask])
    return df2.rolling(LAG).sum()


def analyze(df):
    df = process_df(df)
    df['Buytrigger'] = np.where(gettriggers(df),1,0)
    df['Selltrigger'] = np.where(gettriggers(df, False),1,0)

    # LOGIC TO TRIGGER BUY OR SELL
    df['Buy'] = np.where((df.Buytrigger)  & (df.macd > 0) & (df.rsi > 50),1,0)
    df['Sell'] = np.where((df.Selltrigger) & (df.macd < 0) & (df.rsi < 50),1,0)

    df['Buy'].shift(1)
    df['Sell'].shift(1)
    return df


def get_sub_plot_data(df):
    buy = np.where((df['Buy'] == 1), 1, np.nan) * 0.99 * df['Low'].astype(float)
    sell = np.where((df['Sell'] == 1), 1, np.nan) * 1.01 * df['High'].astype(float)

    ap = []
    if not buy.isnull().all():
        ap.append(mpf.make_addplot(buy, type='scatter', marker='^', markersize=75, color='g'))

    if not sell.isnull().all():
        ap.append(mpf.make_addplot(sell, type='scatter', marker='v', markersize=75, color='r'))

    return ap