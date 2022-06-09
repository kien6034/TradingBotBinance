import asyncio
from src.bot.bot import Bot 
from binance.client import BaseClient
import numpy as np
import pandas as pd 
import sys

bot = Bot('AVAXUSDT', BaseClient.KLINE_INTERVAL_1MINUTE, BaseClient.KLINE_INTERVAL_3MINUTE)
asyncio.run(bot.run())