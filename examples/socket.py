from dotenv import load_dotenv
import os 

load_dotenv()
import asyncio

from binance import AsyncClient, BinanceSocketManager

async def order_book(client, symbol):
    order_book = await client.get_order_book(symbol=symbol)
    print(order_book)


async def kline_listener(client):
    bm = BinanceSocketManager(client)
    symbol = 'BNBBTC'
    res_count = 0
    async with bm.kline_socket(symbol=symbol) as stream:
        while True:
            res = await stream.recv()
            res_count += 1
            print(res)
            if res_count == 5:
                res_count = 0
                loop.call_soon(asyncio.create_task, order_book(client, symbol))

async def main(): 
    client = await AsyncClient.create()
    await kline_listener(client)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())