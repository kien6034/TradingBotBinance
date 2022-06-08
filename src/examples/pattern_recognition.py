from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys


bot = Bot('BTCUSDT', BaseClient.KLINE_INTERVAL_1MINUTE)
data= bot.get_historical_datas()


morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])
data['Morning Star'] = morning_star

morning_star_candle = data[data['Morning Star'] != 0]

for row in morning_star_candle.iterrows():
    print(row)
    new_data= data.iloc[0:row[0] + 1]
    bot.viz(data=new_data)