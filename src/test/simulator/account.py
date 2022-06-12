from cmath import nan
import time
import pandas as pd
import sys
from ...config import RISK
pd.options.mode.chained_assignment = None

class Account:
    def __init__(self, symbol) -> None:
        self.init_balance = 1000
        self.balance = 1000
        self.actual_balance = 1000
        self.symbol = symbol
        self.trading_data = pd.DataFrame()
        self.trading_infos = {
            "total_order": 0,
            "win": 0,
            "lose": 0,
            "performance":0,
        }

        self.on_trading = 0


    def get_balance(self):
        return self.balance

    
    def create_order(self, side, entry, stop_loss, order_size):
        order = {
            "entered_time": time.time(),
            "entry": entry,
            "stop_loss": stop_loss,
            "size": order_size,
            "side": side,
            "close_time": float('nan'),
            'close_price': float('nan'),
            'performance': float('nan')
        }

        if self.trading_data.empty:
            order = {
                "entered_time": [time.time()],
                "entry": [entry],
                "stop_loss": [stop_loss],
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

    def close_order(self, close_price):
        try:
            order = self.trading_data.iloc[-1]
            entry = order['entry'] 
            size = order['size']
            side = order['side']
            performance = self.converse_true_false(side) * (close_price - entry)/entry
            order['close_price'] = close_price
            order['close_time'] = time.time()
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


    ## @param: side: True ~ Long, False: Short
    def get_order_size(self, side, entry, stop_loss):
        w_performance = self.converse_true_false(side) * (stop_loss - entry) / entry
        order_size =  -1* (RISK *self.balance) / w_performance / entry
        return order_size

    ## full sell-buy order
    def place_order(self, side, entry, stop_loss):
        if self.on_trading == 0:
            order_size = self.get_order_size(side, entry, stop_loss)
            # create order 
            self.create_order(side, entry, stop_loss, order_size)

        elif self.on_trading > 0:
            if side == True:
                print("Already in long position")
                return 
            
            self.close_order(entry)

            
        elif self.on_trading < 0:
            if side == False:
                print("Already in short position")
                return 
            
            self.close_order(entry)
       

    def update_order(self, price):
        order = self.trading_data.iloc[-1]
        
        stop_loss = order['stop_loss']
        side = order['side']

        side_value = self.converse_true_false(side)

        if side_value * price <= side_value * stop_loss:
            print(" ++_++ Hit stop loss")
            self.close_order(stop_loss)
    

    ## @dev: Converse true false to 1 and -1
    def converse_true_false(self, side):
        return (-1 + int(side) * 2)


    def get_actual_balance(self, price):
        return self.balance + self.on_trading * price
