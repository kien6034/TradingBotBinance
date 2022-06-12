from cmath import nan
import time
from numpy import take
import pandas as pd
import sys
from ..config import RISK, SAVE_TO_EXCEL
from datetime import datetime
import os

pd.options.mode.chained_assignment = None

class Account:
    def __init__(self, symbol) -> None:
        self.init_balance = 1000
        self.balance = 1000
        self.symbol = symbol
        self.trading_data = pd.DataFrame()
        self.trading_infos = {
            "total_order": 0,
            "win": 0,
            "lose": 0,
            "performance":0,
        }

        self.trade_id = time.time()

        self.on_trading = 0


    def get_balance(self):
        return self.balance

    
    def create_order(self, side, entry, stop_loss, take_profit, order_size, ctime):
 
        order = {
            "entered_time": datetime.fromtimestamp(int(ctime)),
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "size": order_size,
            "side": side,
            "close_time": float('nan'),
            'close_price': float('nan'),
            'performance': float('nan')
        }

        if self.trading_data.empty:
            order = {
                "entered_time": [datetime.fromtimestamp(ctime)],
                "entry": [entry],
                "stop_loss": [stop_loss],
                "take_profit": [take_profit],
                "size": [order_size],
                "side": [side],
                "close_time": [float('nan')],
                'close_price': [float('nan')],
                'performance': [float('nan')]
            }
            self.trading_data = pd.DataFrame(order)
        else:
            self.trading_data = pd.concat([self.trading_data, pd.DataFrame.from_records([order])])

        self.balance -= self.converse_true_false(side) *  entry * order_size
        self.on_trading += self.converse_true_false(side) * order_size
        self.trading_infos["total_order"] += 1

    def close_order(self, close_price, ctime):
        try:
            order = self.trading_data.iloc[-1]
            entry = order['entry'] 
            size = order['size']
            side = order['side']
            performance = self.converse_true_false(side) * (close_price - entry)/entry
            order['close_price'] = close_price
            order['close_time'] = datetime.fromtimestamp(ctime)
            order['performance'] = performance

            self.trading_data.iloc[-1] = order
            self.balance += self.converse_true_false(side)  * size * close_price
        except:
            print("Close order error")
            pass 
       
        if performance > 0:
            self.trading_infos['win'] += 1
        else:
            self.trading_infos['lose'] += 1

        win =  self.trading_infos['win']
        lose = self.trading_infos['lose']
        avg_performance = self.trading_infos['performance']

        self.trading_infos['performance'] = ((win + lose - 1) * (avg_performance ) + performance) / (win + lose)
        self.on_trading = 0

        if SAVE_TO_EXCEL:
            baseDir = os.path.dirname("setup.py")
            dirName = os.path.join(baseDir, f"data/trades/{self.symbol}")
            if not os.path.isdir(dirName):
                os.makedirs(dirName)
            
            self.trading_data.to_csv(f"{dirName}/{self.trade_id}.csv")


    ## @param: side: True ~ Long, False: Short
    def get_order_size(self, side, entry, stop_loss):
        w_performance = self.converse_true_false(side) * (stop_loss - entry) / entry
        order_size =  -1* (RISK *self.balance) / w_performance / entry
        return order_size

    ## full sell-buy order
    def place_order(self, side, entry, stop_loss, take_profit, ctime= None):
        if ctime == None:
            ctime = time.time()

        if self.on_trading == 0:
            order_size = self.get_order_size(side, entry, stop_loss)
            # create order 
            self.create_order(side, entry, stop_loss, take_profit, order_size, ctime)

        elif self.on_trading > 0:
            if side == True:
                return 
            
            self.close_order(entry, ctime)

            
        elif self.on_trading < 0:
            if side == False:
                return 
            
            self.close_order(entry, ctime)
       

    def update_order(self, price, ctime):
        if self.trading_data.empty:
            return 

        order = self.trading_data.iloc[-1]
        if order['close_price'] > 0:
            return 
       

        stop_loss = order['stop_loss']
        take_profit = order['take_profit']
        side = order['side']


        side_value = self.converse_true_false(side)
        
        if stop_loss > 0:
            if side_value * price <= side_value * stop_loss:
                self.close_order(stop_loss, ctime)
        
        if take_profit >0:
            if side_value * price >= side_value * take_profit:
                self.close_order(take_profit, ctime)
    

    ## @dev: Converse true false to 1 and -1
    def converse_true_false(self, side):
        return (-1 + int(side) * 2)


    def get_actual_balance(self, price):
        return self.balance + self.on_trading * price


    