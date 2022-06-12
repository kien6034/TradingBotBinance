from src.test.simulator.account import Account
import sys  


account = Account("BTC")



account.place_order(True, 10, 9)
print(f"10:: {account.balance}")

account.update_order(9)
print(f"13:: {account.balance}")
account.place_order(False, 9, 10)
print(f"Actual_blaance: {account.get_actual_balance(9)}")
print(f"15:: {account.balance}")

account.place_order(True, 5, 6)
print(f"18:: {account.balance}")


print(account.trading_data)
print(account.balance)

