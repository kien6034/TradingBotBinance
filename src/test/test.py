from src.test.simulator.account import Account
import sys  


account = Account("BTC")

account.place_order(1,2)
account.place_order(5,2)

account.close_order(5, 1, 1)

print(account.get_trading_data())
print(account.get_balance())
print(account.get_open_orders())