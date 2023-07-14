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
        trade_shares_quantity = sum(abs(order["Quantity"]) for order in orders_within_trade[symbol] if order["Open/CloseIndicator"] == "O")
        trade_result_percentage = trade_result / trade_amount * 100
        trade_fee = sum(order["IBCommission"] for order in orders_within_trade[symbol])
        trade_enter_date = min(order["DateTime"] for order in orders_within_trade[symbol])
        trade_exit_date = max(order["DateTime"] for order in orders_within_trade[symbol])
        trade_holding_time = trade_exit_date - trade_enter_date

		# Simplify the output based on holding time
        if trade_holding_time.total_seconds() < 60:  # Less than 60 minutes
             seconds_apart = trade_holding_time.total_seconds()
             trade_holding_time_adjusted = str(int(seconds_apart)) + " second" + ("s" if seconds_apart != 1 else "")
        elif trade_holding_time.total_seconds() < 3600:  # Less than 60 minutes
             minutes_apart = trade_holding_time.total_seconds() // 60
             trade_holding_time_adjusted = str(int(minutes_apart)) + " minute" + ("s" if minutes_apart != 1 else "")
        elif trade_enter_date.date() == trade_exit_date.date():  # Same day
             hours_apart = trade_holding_time.total_seconds() // 3600
             trade_holding_time_adjusted = str(int(hours_apart)) + " hour" + ("s" if hours_apart != 1 else "")
        else:  # Different days
             days_apart = (trade_exit_date.date() - trade_enter_date.date()).days
             trade_holding_time_adjusted = str(days_apart) + " day" + ("s" if days_apart != 1 else "")
		
        trades.append({
            "Symbol": symbol,
            "Long/Short": long_short,
            "Quantity": quantity_sum[symbol],
			"Trade Shares/Contracts Quantity": trade_shares_quantity,
            "Trade Result": trade_result,
            "Trade Amount": trade_amount,
            "Trade Result Percentage": trade_result_percentage,
            "Trade Fee": trade_fee,
            "Enter Date": trade_enter_date,
            "Exit Date": trade_exit_date,
			"Holding time": trade_holding_time_adjusted,
            "Orders": orders_within_trade[symbol],
        })
        # Reset for next group
        orders_within_trade[symbol] = []

# Convert to JSON and print
print(json.dumps(trades, indent=2, default=str))

# Write trades to a JSON file
with open("trades.json", "w") as json_file:
    json.dump(trades, json_file, indent=2, default=str)
