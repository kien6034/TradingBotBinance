import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 
import numpy as np
import asyncio
from binance import AsyncClient, BinanceSocketManager
import mplfinance as mpf 
import time
from .utils import get_start_date
from .strategy1 import strategy1

pd.options.mode.chained_assignment = None

NUM_OF_CANDLES = 60
class Bot:
    def __init__(self, symbol, interval) -> None:
        self.trade_token = symbol[0:-4]
        self.base_token = symbol[-4:]
       
        self.symbol = symbol
        self.interval = interval
        secret_key = os.getenv('BINANCE_SECRET')
        api_key = os.getenv('BINANCE_API')
        self.hist_df = None 
        self.start_date = get_start_date(interval)
        self.colums= ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                        'Number of Trades']
        self.client = Client(api_key, secret_key)
        self.loop = asyncio.get_event_loop()

        self.action = 0 ## 1: Longing, 2: Shorting
        self.amount = 2
       

    def get_account_balance(self):
        base_token_balance = self.client.get_asset_balance(asset =self.base_token) 
        trade_token_balance = self.client.get_asset_balance(asset = self.trade_token)
        return (trade_token_balance, base_token_balance)


    def get_future_account_balance(self):
        datas = self.client.futures_account_balance()
        for data in datas:
            if data['asset'] == self.base_token:
                return data['balance']
        return 0

    def get_future_open_position(self):
        print(self.client.futures_recent_trades())
    
    def create_future_market_buy_order(self, quantity):
        try:
            self.client.futures_create_order(symbol=self.symbol, side='BUY', type='MARKET', quantity=quantity)       
        except:
            print("Create order failed")
    
    def create_future_market_sell_order(self, quantity):
        try:
            self.client.futures_create_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=quantity)       
        except:
            print("Create order failed")

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
        self.hist_df = self.hist_df.iloc[-60:]
        status = strategy1(self.hist_df)
        print("New data added \n")
        if status == True:
            print("------------> BUY")
            if self.action == 1: 
                print("-----> already in buy position")
                return
            if self.action == 0:
                #todo: Get quantity herer
                print("-----> OPEN LONG POSITON -----")
                self.create_future_market_buy_order(quantity = self.amount)
                self.action = 1
            # if in buy position 
            elif self.action == 2: 
                print("-----> CLOSE SHORT POSITON -----")
                self.create_future_market_buy_order(quantity = self.amount)
                self.action = 0
            
            self.viz(msg="BUY")
        elif status == False:
            print("-----------> SELL")

            if self.action == 2:
                print("-------> already in sell position")
                return 

            if self.action == 0:
                print("-----> OPEN SHORT POSITON -----")
                self.create_future_market_sell_order(quantity=self.amount)
                self.action = 2
            elif self.action == 1: # longing 
                print("-----> CLOSE LONG POSITON -----")
                self.create_future_market_sell_order(quantity=self.amount)
                self.action = 0

            self.viz(msg="SELL")

        
   

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
        self.get_historical_datas()
        print(self.hist_df.tail(2))
        self.loop.run_until_complete(self.streaming())

    def get_historical_datas(self):
        historical = self.client.get_historical_klines(self.symbol,self.interval, self.start_date * 1000) 
        hist_df = pd.DataFrame(historical)
        '''
        (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
        '''
        hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                            'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']

        self.hist_df = hist_df.drop(columns=['TB Base Volume', 'TB Quote Volume', 'Ignore'])
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
        return [open_time, open, high, low, close, volumn, int(close_time), quote_asset_volume, number_of_trades]
    
    def viz(self, data= None, msg = None):
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
        mav=(10,20,30), savefig = f"data/{self.symbol}/{msg}_{data['Close Time'].iloc[-1]}.jpg")
