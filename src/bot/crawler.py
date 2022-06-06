from dotenv import load_dotenv
import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 


secret_key = os.getenv('BINANCE_SECRET_KEY')
api_key = os.getenv('BINANCE_API_KEY')
client = Client(api_key, secret_key)


historical = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_15MINUTE, '3 day ago UTC')

hist_df = pd.DataFrame(historical)
'''
  (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
'''
hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
print(hist_df.tail())
print(hist_df.shape)