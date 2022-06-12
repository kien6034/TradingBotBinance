import asyncio
from src.bot.bot import Bot 
from binance.client import BaseClient
import numpy as np
import pandas as pd 
import sys

bot = Bot('LUNCBUSD', BaseClient.KLINE_INTERVAL_1MINUTE, BaseClient.KLINE_INTERVAL_3MINUTE)
bot.get_historical_datas()

bot.viz()