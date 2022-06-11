from cmath import nan
import time 
import pandas as pd 
import sys


class Account:
    def __init__(self, symbol) -> None:
        self.init_balance = 1000
        self.balance = 1000 
        self.symbol = symbol
        self.trading_data = pd.DataFrame()
        self.open_orders = []
       

    def get_balance(self):
        return self.balance 

    def get_open_orders(self):
        return self.open_orders

    # Side == True ~~ Long 
    def place_order(self,order_id, entry, side=True):
        size = self.balance / 10 / entry ## enter 10% of the account 
        
        order = {
            "order_id": order_id,
            "entered_time": time.time(),
            "entry": entry,
            "size": size,
            "side": side,
            "close_time": float('nan'),
            'close_price': float('nan'),
        }

        if self.trading_data.empty:
            order = {
                "order_id": [order_id],
                "entered_time": [time.time()],
                "entry": [entry],
                "size": [size],
                "side": [side],
                "close_time": [float('nan')],
                'close_price': [float('nan')]
            }
            self.trading_data = pd.DataFrame(order)
            self.trading_data.set_index("order_id", inplace=True)
        else:
            self.trading_data = pd.concat([self.trading_data, pd.DataFrame.from_records([order])])
            self.trading_data.set_index("order_id", inplace=True)
        
        self.balance -= entry * size 
        self.open_orders.append(order_id)

    def close_order(self, order_id, close_price, close_time):
        try:
            self.trading_data.loc[order_id, ["close_price"]] = [close_price]
            self.trading_data.loc[order_id, ["close_time"]] = [close_time]
            self.open_orders.remove(order_id)
        except:
            print("Order not existed")
            sys.exit()

        self.balance += self.trading_data.loc[order_id]['size']
        

    def get_trading_data(self):
        return self.trading_data

    # def save_trading_data(self):
    #     self.trading_data.to_csv()

    