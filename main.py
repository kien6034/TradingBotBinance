import asyncio
from src.bot.bot import Bot 
from binance.client import BaseClient
import numpy as np
import pandas as pd 
import sys

bot = Bot('AVAXUSDT', BaseClient.KLINE_INTERVAL_1MINUTE)

# bot.get_historical_datas()
# bot.viz()
bot.place_market_buy_order(1)
