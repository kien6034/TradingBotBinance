from dotenv import load_dotenv
import os 

secret_key = os.getenv('BINANCE_SECRET_KEY')
api_key = os.getenv('BINANCE_API_KEY')

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 

client = Client(api_key, secret_key)