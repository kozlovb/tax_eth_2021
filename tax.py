#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from retrieve_data_module import *


# A state entry consists of quantity, time in seconds since epoch and price
# 'Buy', quantity ,date, , price, fee
class StateEntry:
    def __init__(self, operation, qty, date, price, fee):
        self.operation = operation
        self.qty = qty
        self.date = date
        self.price = price
        self.fee = fee


def parse_to_date(line):
    x = line.split()
    year_month_day = x[0].split("-")
    hour_min_sec = x[1].split(":")
    # datetime(year, month, day, hour, minute, second, microsecond)
    return datetime(int(year_month_day[0]), int(year_month_day[1]), int(year_month_day[2]), int(hour_min_sec[0]), int(hour_min_sec[1]), int(hour_min_sec[2]))

#This function reads datainit.txt and data.txt
def read_coinbase_log(file_name):
    trade_int = []
    state_entries = []
    lines  = []
    with open(file_name, 'r') as file1:
        lines = file1.readlines()
    count = 0
    operation = []
    quantities = []
    dates = []
    prices = []
    fees = []

    # read operations
    i = 0
    for j in range(i,len(lines)):
        lines[j] = lines[j].strip()
        lines[j] = lines[j].rstrip()
        if lines[j] != "date":
            if lines[j]:
                buy_sell = lines[j].split()
                for b in buy_sell:
                    operation.append(b)
        else:
            i = j + 1
            break

    # read dates
    for j in range(i,len(lines)):
        lines[j] = lines[j].strip()
        lines[j] = lines[j].rstrip()
        if lines[j] != "quantity":
            if lines[j]:
                dates.append(parse_to_date(lines[j]))
        else:
            i = j + 1
            break

    # read qty
    for j in range(i, len(lines)):
        lines[j] = lines[j].strip()
        lines[j] = lines[j].rstrip()
        if lines[j] != "price":
            quantities.append(float(lines[j]))
        else:
            i = j + 1
            break

    # read price
    for j in range(i, len(lines)):
        lines[j] = lines[j].strip()
        lines[j] = lines[j].rstrip()
        if lines[j] != "fees":
            if lines[j]:
                prices.append(float(lines[j]))
        else:
            i = j + 1
            break

    # read fees
    for j in range(i, len(lines)):
        lines[j] = lines[j].strip()
        lines[j] = lines[j].rstrip()
        if lines[j]:
            fees.append(float(lines[j]))
#register
#          0         1       2       3     4
#trade = ['Buy', quantity ,date, , price, fee]
#register = ['Sell', quantity , date, , price, fee]

    if not (len(operation) == len(dates) == len(quantities) == len(fees) ):
        print("error occured length of various trade parameters are not equal")
        exit()
    for k in range(0, len(operation)):
        trade_int.append([operation[k], quantities[k], dates[k], prices[k], fees[k]])
        #state_entries.append(StateEntry(operation[k], quantities[k], dates[k], prices[k], fees[k]))
    return trade_int

def check_when_balance_0(register):
    sum = 0
    for r in register:
        sum += r[1]
    if sum == 0:
        print("Current sum is ", sum)

#register
#          0         1       2       3     4
#trade = ['Buy', quantity ,date, , price, fee]
#register = ['Sell', quantity , date, , price, fee]

def enter_trade(trade, register):
    balance = 0
    profit = 0
    tmp = []
    if trade[0] == 'BUY':
        tmp = register
        tmp.append(trade)

    if trade[0] == 'SELL':
        indexes_to_del = []
        year = timedelta(days = 365)
        for i in range(0, len(register)):
            if register[i][1] >= trade[1]:
                if trade[2] < register[i][2] + year:
                    profit += (trade[3] - register[i][3]) * trade[1]
                register[i][1] = register[i][1] - trade[1]
                trade[1] = 0
                break
            else:
                if trade[2] < register[i][2] + year:
                    profit += (trade[3] - register[i][3]) * register[i][1]
                trade[1] = trade[1] - register[i][1]
                register[i][1] = 0
                indexes_to_del.append(i)

        for i in range(0, len(register)):
            if i not in indexes_to_del:
                tmp.append(register[i])
    check_when_balance_0(register)
    check_sorted_by_date(tmp)
    return profit, tmp

def read_kraken_log(filename):
    trades = read_coinbase_log(filename)
    # In coinbase trades there is price and in kraken total amount
    # thus here we transform amount to price:
    for t in trades:
        t[3] = t[3]/t[1]
    return trades

def check_sorted_by_date(register):
    if len(register) == 0:
        return
    t_old = register[0][2]
    for t in register:
        if t[2] < t_old:
            print("unsorted date " , t[2], " ", t_old)
            #Lets imagine that trades are adopted to same type loss is basically a sell win is basically a buy.
def pick_trade_update_indexes(index_coinbase, index_kraken_spot, index_kraken_futures, trades_coinbase, trades_kraken_spot, trades_kraken_futures):
    if not (index_coinbase < len(trades_coinbase) or index_kraken_spot < len(trades_kraken_spot) or index_kraken_futures < len(trades_kraken_futures)):
        return None
    indexes_trades = [[index_coinbase, trades_coinbase], [index_kraken_spot, trades_kraken_spot], [index_kraken_futures, trades_kraken_futures]]
    earliest_trade = -1
    for j in range(0,len(indexes_trades)):
        if (indexes_trades[j][0] < len(indexes_trades[j][1])) and earliest_trade < 0:
            earliest_trade = j
        if (indexes_trades[j][0] < len(indexes_trades[j][1])) and (indexes_trades[j][1][indexes_trades[j][0]][2] < indexes_trades[earliest_trade][1][indexes_trades[earliest_trade][0]][2]):
            earliest_trade = j
    trade_to_return = indexes_trades[earliest_trade][1][indexes_trades[earliest_trade][0]]        
    indexes_trades[earliest_trade][0] = indexes_trades[earliest_trade][0] + 1
    return trade_to_return , indexes_trades[0][0], indexes_trades[1][0], indexes_trades[2][0]

def revert_filter_kraken_log(filename):
    f = open(filename, "r")
    lines = f.readlines()
    reverted_lines = []
    for l in lines:
        fields = l.split(',')
        if fields[2] == 'f-eth:usd' and fields[3] == 'futures trade' and fields[4] == 'eth':
            reverted_lines.append(l)
    reverted_lines.reverse()
    return reverted_lines

def futures_to_regular_trades(f_trades, request_price_function):
    trades = []
    futures_gain = 0
    futures_loss = 0
    fee = 0
    
    # winning trade is like BUY trade + taxes for the win
    # loosing trade is like SELL trade of ETH, 
    #          0         1       2       3     4
    #trade = ['Buy', quantity ,date, , price, fee]
    for l in f_trades:
        f_trade = l.split(',')
        pnl  = float(f_trade[11])
        if pnl == 0:
            continue
        date_trade = parse_to_date(f_trade[1])
        price = request_price_function(date_trade.timestamp())
        fee = fee + float(f_trade[12])*price
        trades.append(['SELL', -float(f_trade[12]),date_trade, price, 0])
        if (pnl < 0):
            futures_loss += price * pnl
            trades.append(['SELL', -pnl,date_trade, price, 0])
        else:
            futures_gain += price * pnl
            trades.append(['BUY', pnl, date_trade, price, 0])
    print("trades futures profit " + str(futures_gain))
    print("trades futures loss " + str(futures_loss))
    print("trades futures fee " + str(fee))
    return trades, futures_gain, futures_loss

# Main function here
def calculate(coinbase_trade_files, kraken_spot_file, kraken_futures_file, request_price_function, print_to_file):
    trades_coinbase = []
    register = []
    profit = 0
    error = 0
    for coinbase_log_file in coinbase_trade_files:
        trades_coinbase = trades_coinbase + read_coinbase_log(coinbase_log_file)
    trades_kraken_spot = read_kraken_log(kraken_spot_file)
    trades_kraken_futures_row = revert_filter_kraken_log(kraken_futures_file)
    trades_kraken_futures, futures_profit, futures_loss = futures_to_regular_trades(trades_kraken_futures_row, request_price_function)
    #register
    #          0         1       2       3     4
    #trade = ['BUY', quantity ,date, , price, fee]
    #register = ['SELL', quantity , date, , price, fee]
    
    index_coinbase = 0
    index_kraken_spot = 0
    index_kraken_futures = 0
    while index_coinbase < len(trades_coinbase) or index_kraken_spot < len(trades_kraken_spot) or index_kraken_futures < len(trades_kraken_futures):
        #pick up the earliest of the two
        t, index_coinbase, index_kraken_spot, index_kraken_futures = pick_trade_update_indexes(index_coinbase, index_kraken_spot, index_kraken_futures, trades_coinbase, trades_kraken_spot, trades_kraken_futures)
        trade_profit, register = enter_trade(t, register)
        profit = profit + trade_profit
    if print_to_file:
        f = open(print_to_file, "w")
        for r in register:
            f.write(str(r[0]) +","+ str(r[1]) +","+ str(r[2].timestamp())+","+ str(r[3])+ "\n")
    total_fee = 0
    #no data on fee in kraken
    for t in trades_coinbase:
        total_fee += t[4]
    print("profit", profit)
    print("total_fee", total_fee)

    print("profit minus fee", profit - total_fee)
    return register, futures_profit, futures_loss, profit, total_fee

if __name__ == "__main__":
    coinbase_trade_files = ["datainit.txt", "data1.txt", "data2.txt", "data3.txt"]
    kraken_spot_file = "adapted_ledger_log.txt"
    kraken_futures_file = "kraken_log.txt"
    calculate(coinbase_trade_files, kraken_spot_file, kraken_futures_file, request_price_online, "new_register.txt")

#0 uid,
#1 dateTime,
#2 account,
#3 type,
#4 symbol,
#5 change,
#6 new balance,
#7 new average entry price,
#8 trade price,
#9 mark price,
#10 funding rate,
#11 realized pnl,
#12 fee,
#13 realized funding,
#14 collateral

#0 fdf9aba9-e1de-4ad8-9d3a-9cec164cce20,
#1 2021-04-23 09:26:53,
#2 f-eth:usd,
#3 futures trade,
#4 eth,
#5 0.00905680555,
#6 1.98881098784,
#7 ,
#8 2386.30000000000000000000,
#9 2385.00000000000000000000,
#10,
#11 0.00923281025,
#12 0.00017600470,
#13,
#14 ETH

#0 45dee7e5-eba5-46c9-be07-f80d4f119632,
#1 2021-04-23 09:26:53,
#2 f-eth:usd,
#3 futures trade,
#4 fi_ethusd_210924,
#5 840.00000000000,
#6 -2210.00000000000,
#7 2450.57584784909854005667,
#8 2386.30000000000000000000,
#9 2385.00000000000000000000,,,,,ETH

#0 81a288db-837d-4170-a88d-f813ba5a07cc,
#1 2021-05-18 14:21:24,
#2 f-xbt:usd,
#3 futures trade,
#4 xbt,
#5 -0.00002387926,
#6 0.99482320600,
#7,
#8 44457.00000000000000000000,
#9 44523.75000000000000000000,
#10,
#11 0.00000000000,
#12 0.00002387926,
#13,
#14 XBT
