from distutils.log import error
import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from matplotlib.pyplot import subplot
import pandas as pd 
import numpy as np
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.client import BaseClient
import mplfinance as mpf 
import time
import src.config as config 
import src.bot.utils as utils 

import logging

pd.options.mode.chained_assignment = None

class Bot:
    def __init__(self, symbol, interval, parent_interval) -> None:
        self.trade_token = symbol[0:-4]
        self.base_token = symbol[-4:]
       
        self.symbol = symbol
        self.interval = interval
        self.parent_interval = parent_interval
        secret_key = os.getenv('BINANCE_SECRET')
        api_key = os.getenv('BINANCE_API')
        self.hist_df = None 
        self.parent_hist_df = None
        self.colums= ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                        'Number of Trades']
        self.client = Client(api_key, secret_key)
        self.action = 0 ## 1: Longing, 2: Shorting
        self.amount = 2
        logging.basicConfig(level= logging.INFO,filename='app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        self.loop = asyncio.get_event_loop()
       

    ## API Call 
    async def process_new_data(self, res, interval):
        data = self.refine_data(res)
        print(f"========= {interval} ========== \n")
        if interval == self.parent_interval:
            df_len = len(self.parent_hist_df)
            self.parent_hist_df.loc[df_len] = data
            self.parent_hist_df = self.parent_hist_df.iloc[-config.NUM_OF_CANDLES:]
            return

        print(f"{res}")
        # df_len= len(self.hist_df)
        # self.hist_df.loc[df_len] = data
        # self.hist_df = self.hist_df.iloc[-config.NUM_OF_CANDLES:]
        # status = strategy1(self.hist_df)

        # if status == True:
        #     logging.info('===========> CAN BUY')
        #     logging.info(f"Enter price: {self.hist_df.iloc[-1]}")
        #     if self.action == 1: 
        #         logging.info('---> Already in longing postion')
        #         return
        #     if self.action == 0:
        #         #todo: Get quantity herer
        #         logging.info("---> Open long position")
        #         #self.create_future_market_buy_order(quantity = self.amount)
        #         self.action = 1
        #     # if in buy position 
        #     elif self.action == 2: 
        #         logging.info("---> Close short position")
        #         #self.create_future_market_buy_order(quantity = self.amount)
        #         self.action = 0
            
        #     logging.info('------------------ \n')
        #     self.viz(msg="BUY")
        # elif status == False:
        #     logging.info("===========> SELL")
        #     logging.info(f"Enter price: {self.hist_df.iloc[-1]}")

        #     if self.action == 2:
        #         logging.info("---> already in sell position")
        #         return 

        #     if self.action == 0:
        #         logging.info("-----> open short position")
        #         #self.create_future_market_sell_order(quantity=self.amount)
        #         self.action = 2
        #     elif self.action == 1: # longing 
        #         logging.info("----->  Close long position")
        #         #self.create_future_market_sell_order(quantity=self.amount)
        #         self.action = 0

        #     logging.info('------------------ \n')
        #     self.viz(msg="SELL")

    ## Streaming 
    async def kline_listener(self,client, interval):
        bm = BinanceSocketManager(client)
        async with bm.kline_socket(symbol=self.symbol, interval=interval) as stream:
            while True:
                res = await stream.recv()

                if res['k']['x'] == True:
                    await self.process_new_data(res, interval)
              
    async def streaming(self, interval):
        client = await AsyncClient.create()
        await self.kline_listener(client, interval)

    async def run(self):
        self.get_historical_datas()
        self.get_historical_datas(self.parent_interval)
        print(self.hist_df.tail(2))
        print(self.parent_hist_df.tail(2))
        all_runs = [self.streaming(self.interval), self.streaming(self.parent_interval)]
        await asyncio.gather(*all_runs)

    def get_historical_datas(self, interval = None):
        '''
        (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
        '''
        columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                            'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
        if interval == None:
            historical = self.client.get_historical_klines(self.symbol,self.interval,(int(time.time()) - utils.get_time_diff(self.interval)) * 1000) 
            hist_df = pd.DataFrame(historical)
            hist_df.columns = columns
            self.hist_df = hist_df.drop(columns=['TB Base Volume', 'TB Quote Volume', 'Ignore'])
            return self.hist_df
        
        if interval  == self.parent_interval:
            historical = self.client.get_historical_klines(self.symbol,self.parent_interval, (int(time.time()) - utils.get_time_diff(self.parent_interval))* 1000) 
            hist_df = pd.DataFrame(historical)
            hist_df.columns = columns
            self.parent_hist_df = hist_df.drop(columns=['TB Base Volume', 'TB Quote Volume', 'Ignore'])
            return self.parent_hist_df
        


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
        return [open_time, open, high, low, close, volumn, int(close_time), quote_asset_volume, number_of_trades]
    
    def viz(self, data=pd.DataFrame(), msg = None, hlines = [], addplot =[]):
        if data.empty:
            data= self.hist_df

        data['Open Time'] = pd.to_datetime(data['Open Time']/1000, unit='s')
        data['Close Time'] = pd.to_datetime(data['Close Time']/1000, unit='s')
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume']
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, axis=1)
        data.set_index('Close Time')

        baseDir = os.path.dirname("setup.py")
        dirName = os.path.join(baseDir, f"data/{self.symbol}")
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
    
      
        mpf.plot(
            data.set_index('Close Time'), 
            type='candle', 
            style='charles', 
            volume=True, 
            title=f"{self.symbol} Last {self.interval}", 
            mav=(10,20,30), 
            savefig = f"data/{self.symbol}/{msg}_{data['Close Time'].iloc[-1]}.jpg",
            hlines=dict(hlines = hlines, linewidths=2,alpha=0.4),
            addplot=addplot
        )
