from distutils.log import error
from posixpath import dirname
import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 
import numpy as np
import asyncio
from binance import AsyncClient, BinanceSocketManager
import mplfinance as mpf 
import time
from .utils import get_start_date

pd.options.mode.chained_assignment = None

NUM_OF_CANDLES = 60
class Bot:
    def __init__(self, symbol, interval) -> None:
        self.symbol = symbol
        self.interval = interval
        secret_key = os.getenv('BINANCE_SECRET')
        api_key = os.getenv('BINANCE_API')
        self.hist_df = None 
        self.start_date = get_start_date(interval)
        
        self.colums= ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                        'Number of Trades']
        self.client = Client(api_key, secret_key)
        print(self.client.get_asset_balance(asset='USDT'))
        self.loop = asyncio.get_event_loop()
       
       
    def place_market_buy_order(self, quantity):
        try:
            order = self.client.order_market_buy(
                symbol = self.symbol,
                quantity= quantity
            )
            print(order)
        except error:
            print(error)


    def place_market_sell_order(self, quantity):
        try:
            order = self.client.order_market_sell(
                symbol = self.symbol,
                quantity= quantity
            )
            print(order)
        except error:
            print(error)

    ## API Call 
    async def process_new_data(self,res):
        data = self.refine_data(res)
        data_length= len(self.hist_df)
        self.hist_df.loc[data_length] = data
        
   

    ## Streaming 
    async def kline_listener(self,client):
        bm = BinanceSocketManager(client)
        async with bm.kline_socket(symbol=self.symbol, interval=self.interval) as stream:
            while True:
                res = await stream.recv()
                if res['k']['x'] == True:
                    self.loop.call_soon(asyncio.create_task, self.process_new_data(res))
              
    async def streaming(self):
        client = await AsyncClient.create()
        await self.kline_listener(client)

    def run(self):
        self.loop.run_until_complete(self.streaming())

    def get_historical_datas(self):
        print("went here")
        historical = self.client.get_historical_klines(self.symbol,self.interval, self.start_date * 1000) 
        hist_df = pd.DataFrame(historical)
        '''
        (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
        '''
        hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                            'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']

        self.hist_df = hist_df.drop(columns=['TB Base Volume', 'TB Quote Volume', 'Ignore'])
        print(self.hist_df)
        return self.hist_df


    def refine_data(self,res):
        open_time =  res['k']['t']
        open = res['k']['o']
        close = res['k']['c']
        high= res['k']['h']
        low = res['k']['l']
        volumn = res['k']['v']
        close_time = res['k']['T']
        quote_asset_volume=  res['k']['q']
        number_of_trades = res['k']['n']
        return [open_time, open, high, low, close, volumn, close_time, quote_asset_volume, number_of_trades]
    
    def viz(self, data= None):
        if data == None:
            data= self.hist_df

        data['Open Time'] = pd.to_datetime(data['Open Time']/1000, unit='s')
        data['Close Time'] = pd.to_datetime(data['Close Time']/1000, unit='s')
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume']
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, axis=1)
        data.set_index('Close Time').tail(100)

        baseDir = os.path.dirname("setup.py")
        dirName = os.path.join(baseDir, f"data/{self.symbol}")
        if not os.path.isdir(dirName):
            pass
            os.makedirs(dirName)

        mpf.plot(data.set_index('Close Time').tail(120), 
        type='candle', style='charles', 
        volume=True, 
        title=f"{self.symbol} Last {self.interval}", 
        mav=(10,20,30), savefig = f"data/{self.symbol}/{data['Close Time'].iloc[-1]}.jpg")