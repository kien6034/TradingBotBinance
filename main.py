import asyncio
from bot.bot import Bot 
from binance.client import BaseClient
import numpy as np
import pandas as pd 
import sys


bot = Bot('BTCUSDT', BaseClient.KLINE_INTERVAL_1MINUTE)

bot.get_historical_datas()
bot.viz()