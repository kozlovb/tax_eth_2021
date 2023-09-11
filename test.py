from tax import *
from datetime import datetime

def is_close(a, b,):
    return abs(a - b) <= 1e-08

# coinbase spot
'''
BUY
BUY
SELL
date
2018-01-01 00:00:00
2021-01-01 00:00:00
2021-11-30 00:00:00
quantity
0.5
2.0
0.5
price
300
800
900
fees
1
1
1
'''
# kraken spot
'''
SELL
date
2021-02-01 00:00:00
quantity
0.7
price
700
fees
0.0
'''
# futures kraken
'''
uid,dateTime,account,type,symbol,change,new balance,new average entry price,trade price,mark price,funding rate,realized pnl,fee,realized funding,collateral
1,2021-02-01 08:19:06,f-eth:usd,futures trade,eth,-0.00000916188,0.99976732317,,2728.70000000000000000000,2731.40000000000000000000,,-0.1,0.00000916188,,ETH
2,2021-12-01 08:19:06,f-eth:usd,futures trade,eth,-0.00000916188,0.99976732317,,2728.70000000000000000000,2731.40000000000000000000,,0.05,0.00000916188,,ETH
'''

coinbase_trade_files = ["/Users/bkozlov/Tax2021Repo/tax_eth_2021/data_coinbase_test.txt"]
kraken_spot_file = "/Users/bkozlov/Tax2021Repo/tax_eth_2021/adapted_ledger_log_test.txt"
kraken_futures_file = "/Users/bkozlov/Tax2021Repo/tax_eth_2021/kraken_log_test.txt"
def mocked_price(any):
    return 500
result_state, futures_profit, futures_loss, taxable_profit, total_fee = calculate(coinbase_trade_files, kraken_spot_file, kraken_futures_file, mocked_price, None)

#win 0.05*500 = 25.0
assert is_close(futures_profit, 25.0)
#loss -0.1*500 = -50.0
assert is_close(futures_loss, -50.0)
# initial state
# 2018-01-01, 0.5 for 300 
# 2021-01-01, 2.0 for 800   fee = 2
# calculateby by hand 
# sell kraken spot 0.7 , price is 700/0.7=1000, (1000-300)*0.5 profit not taxed, taxed = (1000-800)*0.2= 40
# state:
# 2021-01-01, 1.8 for 800
# loss futures kraken (sold 0.1 for 500)  (500-800)*0.1=-30 , taxed = 10
# state:
# 2021-01-01, 1.7 for 800
# sell coinbase 0.5 for 900 so (900-800)*0.5=50 , taxed = 60
# state:
# 2021-01-01, 1.2 for 800 
# win futures kraken 0.05 for 500 
# state:
# 2021-01-01 00:00:00 1.2 for 800
# 2021-12-01 08:19:06 0.05 for 500

assert is_close(taxable_profit,60)
assert is_close(total_fee, 3)

#CHECK FINAL STATE
assert len(result_state) == 2
#assert result_state[0][0] == 'BUY' and is_close(result_state[0][1], 1.2) and datetime(2021, 1, 1, 0, 0, 0) == result_state[0][2] and is_close(result_state[0][3], 800)
#assert result_state[1][0] == 'BUY' and is_close(result_state[1][1], 0.05) and datetime(2021, 12, 1, 8, 19, 6) == result_state[1][2]  and is_close(result_state[1][3], 500)
