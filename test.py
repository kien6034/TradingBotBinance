from urllib.parse import parse_qs
from binance import AsyncClient, BinanceSocketManager
from binance.client import BaseClient

import asyncio
async def run_it(interval):
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    
    async with bm.kline_socket(symbol='BTCUSDT', interval=interval) as stream:
            while True:
                print(f"Getting streaming data for {interval}")
                res = await stream.recv()
                print(res)

async def main():
    all_runs = [run_it(BaseClient.KLINE_INTERVAL_1MINUTE), run_it(BaseClient.KLINE_INTERVAL_3MINUTE)]
    await asyncio.gather(*all_runs)


asyncio.run(main())
