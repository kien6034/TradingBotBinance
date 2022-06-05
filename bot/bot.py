from dotenv import load_dotenv
import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 
import numpy as np
import asyncio
from binance import AsyncClient, BinanceSocketManager
import mplfinance as mpf 



class Bot:
    def __init__(self, symbol, interval) -> None:
        self.symbol = symbol
        self.interval = interval
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        api_key = os.getenv('BINANCE_API_KEY')
        self.client = Client(api_key, secret_key)
        self.loop = asyncio.get_event_loop()
        self.colums= ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                            'Number of Trades']

        self.hist_df = None 
    

    ## API Call 
    async def process_new_data(self,res):
        data = self.refine_data(res)
        data_length= len(self.hist_df)
        self.hist_df.loc[data_length] = data
        print(self.hist_df.tail(2))
        
   

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
        historical = self.client.get_historical_klines('BTCUSDT',self.interval, '1 day ago UTC') 
        hist_df = pd.DataFrame(historical)
        '''
        (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
        '''
        hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                            'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']

        self.hist_df = hist_df.drop(columns=['TB Base Volume', 'TB Quote Volume', 'Ignore'])
        print( self.hist_df.tail(2))
        print(self.hist_df.shape)


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
        
   
    def viz(self):
        self.hist_df['Open Time'] = pd.to_datetime(self.hist_df['Open Time']/1000, unit='s')
        self.hist_df['Close Time'] = pd.to_datetime(self.hist_df['Close Time']/1000, unit='s')
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume']
        self.hist_df[numeric_columns] = self.hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
        self.hist_df.set_index('Close Time').tail(100)
        

        mpf.plot(self.hist_df.set_index('Close Time').tail(120), 
        type='candle', style='charles', 
        volume=True, 
        title='ETHBTC Last 120 Days', 
        mav=(10,20,30), savefig = 'testimage.jpg')
