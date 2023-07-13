import csv
import json
import datetime

# Read CSV data from file
with open("orders.csv", newline="") as orders_file:
    csv_reader = csv.DictReader(orders_file)
    orders = [row for row in csv_reader]

# Separate timezone from DateTime and add to another column
for order in orders:
    date_time = datetime.datetime.strptime(order["DateTime"].split(" ")[0], "%Y-%m-%d;%H:%M:%S")
    timezone = order["DateTime"].split(" ")[1]
    order["DateTime"] = date_time
    order["TimeZone"] = timezone
    order["Quantity"] = int(order["Quantity"]) # Ensure  is integer
    order["TradePrice"] = float(order["TradePrice"]) # Ensure  is float
    order["TradeMoney"] = float(order["TradeMoney"]) # Ensure  is float
    order["IBCommission"] = float(order["IBCommission"]) # Ensure  is float
    order["NetCash"] = float(order["NetCash"]) # Ensure  is float
    order["CostBasis"] = float(order["CostBasis"]) # Ensure  is float

# Sort the orders by DateTime
orders = sorted(orders, key=lambda k: k["DateTime"])

# Write trades to a JSON file
with open("orders.json", "w") as json_file:
    json.dump(orders, json_file, indent=2, default=str)

# Group the orders by symbol and sum quantity
trades = []
quantity_sum = {}
net_cash_sum = {} 
orders_within_trade = {}
trade_dates = {}  # New dictionary to hold the trade dates

for order in orders:
    symbol = order["Symbol"]
    quantity = order["Quantity"]
    net_cash = order["NetCash"]
    date_time = order["DateTime"]

    if symbol not in quantity_sum:
        quantity_sum[symbol] = 0
        net_cash_sum[symbol] = 0.0 
        orders_within_trade[symbol] = []
        trade_dates[symbol] = []  # Initialize list for this symbol

    quantity_sum[symbol] += quantity
    net_cash_sum[symbol] += net_cash 
    orders_within_trade[symbol].append(order)
    trade_dates[symbol].append(date_time)  # Add date to the list

    if quantity_sum[symbol] == 0:
        trades.append({
            "Symbol": symbol,
            "Quantity": quantity_sum[symbol],
            "Trade Result": net_cash_sum[symbol],
            "Orders": orders_within_trade[symbol],
            "TradeDates": trade_dates[symbol]  # Add this line to include the dates in the output
        })
        # Reset for next group
        orders_within_trade[symbol] = []  
        net_cash_sum[symbol] = 0.0 # reset the running net cash for this symbol
        trade_dates[symbol] = []  # reset the dates list for this symbol

# Convert to JSON and print
print(json.dumps(trades, indent=2, default=str))

# Write trades to a JSON file
with open("trades.json", "w") as json_file:
    json.dump(trades, json_file, indent=2, default=str)
