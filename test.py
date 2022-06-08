import logging

class Bot:
    def __init__(self) -> None:
        logging.basicConfig(level= logging.DEBUG,filename='app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


    def log(self):
        logging.debug('This will get logged to a file')


bot= Bot()
bot.log()