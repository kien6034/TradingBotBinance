from ..config import LONG_RSI_TIMEFRAME, SHORT_RSI_TIMEFRAME, EMA_TIMEFRAME
import talib

"""
    - Using EMA + RSI 
"""

def strategy1(hist_df):
    data = hist_df["Close"]
    rsi_short = talib.RSI(data, SHORT_RSI_TIMEFRAME)
    rsi_long = talib.RSI(data, LONG_RSI_TIMEFRAME)

    # calculating ema from rsi 
    ema_short = talib.EMA(rsi_short, EMA_TIMEFRAME)
    ema_long = talib.EMA(rsi_long, EMA_TIMEFRAME) 
   
    # conditions 
    if((ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] < ema_long.iloc[-2])):
        return True

    if((ema_long.iloc[-1] > ema_short.iloc[-1] and ema_long.iloc[-2] < ema_short.iloc[-2])):
        return False

    return None 

