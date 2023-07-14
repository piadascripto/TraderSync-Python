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
    order["Quantity"] = int(order["Quantity"])  # Ensure quantity is integer
    order["TradePrice"] = float(order["TradePrice"])  # Ensure TradePrice is float
    order["TradeMoney"] = float(order["TradeMoney"])  # Ensure TradeMoney is float
    order["IBCommission"] = float(order["IBCommission"])  # Ensure IBCommission is float
    order["NetCash"] = float(order["NetCash"])  # Ensure NetCash is float
    order["CostBasis"] = float(order["CostBasis"])  # Ensure CostBasis is float

# Sort the orders by DateTime
orders = sorted(orders, key=lambda k: k["DateTime"])

# Write trades to a JSON file
with open("orders.json", "w") as json_file:
    json.dump(orders, json_file, indent=2, default=str)

# Group the orders by symbol and sum quantity
trades = []
quantity_sum = {}
orders_within_trade = {}

for order in orders:
    symbol = order["Symbol"]
    quantity = order["Quantity"]

    if symbol not in quantity_sum:
        quantity_sum[symbol] = 0
        orders_within_trade[symbol] = []

    quantity_sum[symbol] += quantity
    orders_within_trade[symbol].append(order)

    if quantity_sum[symbol] == 0:
        long_short = "LONG" if orders_within_trade[symbol][0]["Open/CloseIndicator"] == "O" and orders_within_trade[symbol][0]["Buy/Sell"] == "BUY" else "SHORT"
        trade_result = sum(order["NetCash"] for order in orders_within_trade[symbol])
        trade_amount = sum(abs(order["TradeMoney"]) for order in orders_within_trade[symbol] if order["Open/CloseIndicator"] == "O")
        trade_result_percentage = trade_result / trade_amount * 100
        trade_fee = sum(order["IBCommission"] for order in orders_within_trade[symbol])
        trades.append({
            "Symbol": symbol,
            "Long/Short": long_short,
            "Quantity": quantity_sum[symbol],
            "Trade Result": trade_result,
            "Trade Amount": trade_amount,
            "Trade Result Percentage": trade_result_percentage,
            "Trade Fee": trade_fee,
            "Enter Date": min(order["DateTime"] for order in orders_within_trade[symbol]),
            "Exit Date": max(order["DateTime"] for order in orders_within_trade[symbol]),
            "Orders": orders_within_trade[symbol],
        })
        # Reset for next group
        orders_within_trade[symbol] = []

# Convert to JSON and print
print(json.dumps(trades, indent=2, default=str))

# Write trades to a JSON file
with open("trades.json", "w") as json_file:
    json.dump(trades, json_file, indent=2, default=str)
