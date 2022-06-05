from dotenv import load_dotenv
import os 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd 

import asyncio
from binance import AsyncClient, BinanceSocketManager



class Bot:
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        api_key = os.getenv('BINANCE_API_KEY')
        self.client = Client(api_key, secret_key)
        self.loop = asyncio.get_event_loop()
    

    ## API Call 
    async def order_book(client, symbol):
        order_book = await client.get_order_book(symbol=symbol)
        print(order_book)

    ## Streaming 
    async def kline_listener(self,client):
        bm = BinanceSocketManager(client)
        res_count = 0
        async with bm.kline_socket(symbol=self.symbol) as stream:
            while True:
                res = await stream.recv()
                res_count += 1
                print(res)
                if res_count == 5:
                    res_count = 0
                    self.loop.call_soon(asyncio.create_task, self.order_book(client, self.symbol))
    
    async def streaming(self):
        client = await AsyncClient.create()
        await self.kline_listener(client)

    def run(self):
        self.loop.run_until_complete(self.streaming())

    def get_historical_datas(self):
        historical = self.client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_15MINUTE, '3 day ago UTC') 
        return historical


