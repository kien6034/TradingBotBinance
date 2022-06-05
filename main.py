import asyncio
from bot.bot import Bot 

async def async_func():
  
    bot = Bot('BTCUSDT')
    bot2 = Bot('BNBUSDT')

    bot2.run()
    bot.run()

loop = asyncio.get_event_loop()
coroutine = async_func()
loop.run_until_complete(coroutine)


