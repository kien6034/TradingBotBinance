from src.bot.bot import Bot
from binance.client import BaseClient
import talib
import sys


bot = Bot('BTCUSDT', BaseClient.KLINE_INTERVAL_1HOUR)
data= bot.get_historical_datas()

morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])
data['Morning Star'] = morning_star

morning_star_candle = data[data['Morning Star'] != 0]
index0 = morning_star_candle.iloc[0].name

data2 = data.iloc[0:index0 +1]
morning_star2 = talib.CDLMORNINGSTAR(data2['Open'], data2['High'], data2['Low'], data2['Close'])
data['Morning Star'] = morning_star2

morning_star_candle_2 = data2[data2['Morning Star'] != 0]
print(morning_star_candle_2)


sys.exit()

for row in morning_star_candle.iterrows():
    new_data= data.iloc[0:row[0] + 1]
    bot.viz(data=new_data)