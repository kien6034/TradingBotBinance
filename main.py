import asyncio
from src.bot.bot import Bot 
from binance.client import BaseClient
import numpy as np
import pandas as pd 
import sys

bot = Bot('AVAXUSDT', BaseClient.KLINE_INTERVAL_1MINUTE)
bot.test()