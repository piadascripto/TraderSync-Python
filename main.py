import csv
import json
import datetime
from utils import simplify_time_difference
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Read CSV data from file
with open("orders.csv", newline="") as orders_file:
    csv_reader = csv.DictReader(orders_file)
    orders = [row for row in csv_reader]


def create_trades(orders): 
	# Separate timezone from DateTime and add to another column
	for order in orders:
	    date_time = datetime.datetime.strptime(order["DateTime"].split(" ")[0], "%Y-%m-%d;%H:%M:%S")
	    timezone = order["DateTime"].split(" ")[1]
	    order["TimeZone"] = timezone
	    #date_time = datetime.datetime.strptime(order["DateTime"].split(" ")[0], "%Y-%m-%d;%H:%M:%S")
	    order["DateTime"] = date_time
	
		
	    order["Quantity"] = float(order["Quantity"])  # Ensure quantity is integer
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
	        trade_result_percentage = trade_result / trade_amount
	        win_loss = "WIN" if trade_result > 0 else "LOSS"
	        trade_fee = sum(order["IBCommission"] for order in orders_within_trade[symbol])
	        trade_asset = orders_within_trade[symbol][0]["AssetClass"]
	        trade_enter_date = min(order["DateTime"] for order in orders_within_trade[symbol])
	        trade_exit_date = max(order["DateTime"] for order in orders_within_trade[symbol])
			
	        trades.append({
	            "Symbol": symbol,
	            "Asset class": trade_asset,
	            "Long/Short": long_short,
				"Win/Loss": win_loss,
	            "Number of Orders": len(orders_within_trade[symbol]),
	            "Quantity": quantity_sum[symbol],
				"Trade Shares/Contracts Quantity": trade_shares_quantity,
	            "Trade Result": trade_result,
	            "Trade Amount": trade_amount,
	            "Trade Result Percentage": trade_result_percentage,
	            "Trade Fee": trade_fee,
	            "Enter Date": trade_enter_date,
	            "Exit Date": trade_exit_date,
				"Holding time": simplify_time_difference(trade_enter_date, trade_exit_date),
	            "Orders": orders_within_trade[symbol],
	        })
	        # Reset for next group
	        orders_within_trade[symbol] = []
	
	# Convert to JSON and print
	#print(json.dumps(trades, indent=2, default=str))
	
	# Write trades to a JSON file
	with open("trades.json", "w") as json_file:
	    json.dump(trades, json_file, indent=2, default=str)

	return trades

trades = create_trades(orders)

def create_trades_journal(trades):
	
	trades_journal = {}
	
	for trade in trades:
	    trade_day = trade['Exit Date'].date().isoformat()   # Extract only the date portion
	
	    trade_data = {
	        "Symbol": trade["Symbol"],
	        "Asset class": trade["Asset class"],
	        "Long/Short": trade["Long/Short"],
	        "Win/Loss": trade["Win/Loss"],
	        "Number of Orders": trade["Number of Orders"],
	        "Quantity": trade["Quantity"],
	        "Trade Shares/Contracts Quantity": trade["Trade Shares/Contracts Quantity"],
	        "Trade Result": trade["Trade Result"],
	        "Trade Amount": trade["Trade Amount"],
	        "Trade Result Percentage": trade["Trade Result Percentage"],
	        "Trade Fee": trade["Trade Fee"],
	        "Enter Date": trade["Enter Date"],
	        "Exit Date": trade["Exit Date"],
	        "Holding time": trade["Holding time"]
	    }
	
	    if trade_day in trades_journal:
	        trades_journal[trade_day]["Total Result"] += trade["Trade Result"]
	        trades_journal[trade_day]["Total Fee"] += trade["Trade Fee"]
	        trades_journal[trade_day]["Total Amount"] += trade["Trade Amount"]
	        trades_journal[trade_day]["Number of Trades"] += 1
	        if trade["Trade Result"] > 0:
	            trades_journal[trade_day]["Total Gains"] += trade["Trade Result"]
	        elif trade["Trade Result"] < 0:
	            trades_journal[trade_day]["Total Losses"] += trade["Trade Result"]
	        if trade["Win/Loss"] == "WIN":
	            trades_journal[trade_day]['Number of Wins'] += 1
	        elif trade["Win/Loss"] == "LOSS":
	            trades_journal[trade_day]['Number of Loss'] += 1
	        trades_journal[trade_day]["Trades"].append(trade_data)
			
	    else:
	        trades_journal[trade_day] = {
				"Total Result": trade["Trade Result"],
				"Total Result Percentaage": 0,
	            "Total Amount": trade["Trade Amount"],
				"Profit factor": 0,
				"Total Gains" : trade["Trade Result"] if trade["Trade Result"] > 0 else 0.0,
	            "Total Losses" : (trade["Trade Result"] if trade["Trade Result"] < 0 else 0.0),
	            "Total Fee": trade["Trade Fee"],
	            "Number of Trades": 1,
	            "Average Trade Amount": 0,
	
	            "Win Rate": 1.0 if trade["Win/Loss"] == "WIN" else 0.0,
	            "Number of Wins": 1 if trade["Win/Loss"] == "WIN" else 0,
	            "Number of Loss": 1 if trade["Win/Loss"] == "LOSS" else 0,
				"Trade day": trade_day,
	            "Trades": [trade_data]
	        }
	
	     # Calculating more statisctis 
	    trades_journal[trade_day]["Total Result Percentaage"] = trades_journal[trade_day]["Total Result"] / trades_journal[trade_day]["Total Amount"]
	    trades_journal[trade_day]["Average Trade Amount"] = trades_journal[trade_day]["Total Amount"] / trades_journal[trade_day]["Number of Trades"]
	    trades_journal[trade_day]["Win Rate"] = trades_journal[trade_day]["Number of Wins"] / trades_journal[trade_day]["Number of Trades"]
		# Write trades_journal to a JSON file
	with open("trades_journal.json", "w") as json_file:
	    json.dump(trades_journal, json_file, indent=2, default=str)

	return trades_journal

trades_journal = create_trades_journal(trades)

def create_trades_statitics(trades_journal):

	#key aggregated statics
	
	all_result = 0
	all_gains = 0
	all_losses = 0
	all_profit_factor = 0
	all_win_rate = 0
	all_win = 0
	all_loss = 0
	all_fee = 0
	all_amount = 0
	
	for day in trades_journal:
	    all_result += trades_journal[day]["Total Result"]
	    all_gains += trades_journal[day]["Total Gains"]
	    all_losses += abs(trades_journal[day]["Total Losses"])
	    all_amount += trades_journal[day]["Total Amount"]
	    all_profit_factor = (all_gains / all_losses) if all_losses != 0 else None
	    all_win += trades_journal[day]["Number of Wins"]
	    all_loss += trades_journal[day]['Number of Loss']
	    all_win_rate = all_win / (all_loss + all_win)
	    all_fee += trades_journal[day]["Total Fee"]
	
	trades_statistics = {
	    "Net Result": all_result, 
		"Net Gains $": all_gains,
	    "Net Losses $": all_losses,
	    "Return %": all_result / all_amount,
		"Average Amount": all_amount / (all_win + all_loss),
		"Profit Factor": all_profit_factor,
		"Win Rate %": all_win_rate,
		"# Wins": all_win,
		"# Loss": all_loss,
		"Fees": all_fee,
		
	}
	# Convert to JSON and print
	print(json.dumps(trades_statistics, indent=2, default=str))
	
	# Write trades_journal to a JSON file
	with open("trades_statistics.json", "w") as json_file:
	    json.dump(trades_statistics, json_file, indent=2, default=str)

	return trades_statistics

create_trades_statitics(trades_journal)

def create_chart_trade_result_by_day(trades_journal):
    # Convert trades_journal to a DataFrame
    trades_df = pd.DataFrame(trades_journal).T

    # Reset the index to convert the trade_day (index) to a column
    trades_df.reset_index(level=0, inplace=True)

    # Convert the "Total Result" column to numeric (float) type
    trades_df["Total Result"] = pd.to_numeric(trades_df["Total Result"])

    # Sort the DataFrame by trade_day (index) in ascending order
    trades_df.sort_values(by="index", ascending=True, inplace=True)

    # Create a new column "Color" to determine the color of the bars based on the value of "Total Result"
    trades_df["Color"] = trades_df["Total Result"].apply(lambda x: "#00FF00" if x >= 0 else "#FF0000")

    # Create the chart using pandas plot
    trades_df.plot(x="index", y="Total Result", kind="bar", title="Total Result by Trade Day", color=trades_df["Color"])

    # Show the chart
    plt.show()

def create_chart_cumulative_trade_result_by_day(trades_journal):
    # Convert trades_journal to a DataFrame
    trades_df = pd.DataFrame(trades_journal).T

    # Reset the index to convert the trade_day (index) to a column
    trades_df.reset_index(level=0, inplace=True)

    # Convert the "Total Result" column to numeric (float) type
    trades_df["Total Result"] = pd.to_numeric(trades_df["Total Result"])

    # Sort the DataFrame by trade_day (index) in ascending order
    trades_df.sort_values(by="index", ascending=True, inplace=True)

    # Calculate the cumulative result
    trades_df["Cumulative Result"] = trades_df["Total Result"].cumsum()

    # Determine the color based on the cumulative result
    trades_df["Color"] = trades_df["Cumulative Result"].apply(lambda x: "#00FF00" if x >= 0 else "#FF0000")

    # Create the chart showing the cumulative total result
    trades_df.plot(x="index", y="Cumulative Result", kind="bar", title="Cumulative Total Result", color=trades_df["Color"])

    # Show the chart
    plt.show()

def create_chart_calendar_heatmap_trade_result_by_day(trades_journal):
    # Convert to DataFrame
    df = pd.DataFrame(trades_journal).T
    df['Trade day'] = pd.to_datetime(df['Trade day'])
    df['Week'] = df['Trade day'].dt.isocalendar().week
    df['Day'] = df['Trade day'].dt.day_name()

    # Pivot the table for both Total Result and Trade Day
    heatmap_trade_result_data = df.pivot(index='Week', columns='Day', values='Total Result').fillna(0)
    trade_days_data = df.pivot(index='Week', columns='Day', values='Trade day').fillna('')
    number_of_trades_data = df.pivot(index='Week', columns='Day', values='Number of Trades').fillna(0)

    # Order the days if they exist
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    available_days = [day for day in days_of_week if day in heatmap_trade_result_data.columns]
    heatmap_trade_result_data = heatmap_trade_result_data[available_days]
    trade_days_data = trade_days_data[available_days]
    number_of_trades_data = number_of_trades_data[available_days]
	
    # Plot
    fig, ax = plt.subplots(figsize=(7, 7))
    mask = (number_of_trades_data.isnull())

	# Define the custom colormap with a spectral transition from red to green, passing through white
    colors = ["#FF0000", "#FFFFFF", "#00FF00"]
    cmap = sns.blend_palette(colors, as_cmap=True, n_colors=256)

    # Set the background color for the masked cells to white
    ax.set_facecolor('white')

    
    sns.heatmap(heatmap_trade_result_data, cmap=cmap, center=0, annot=True, fmt=".2f", cbar=False, mask=mask, square=True, ax=ax, linewidths=.5)
    
    # Adjust annotations
    for text, trade_day, num_trades in zip(ax.texts, trade_days_data.values.ravel(), number_of_trades_data.values.ravel()):

        trade_result = float(text.get_text())
        
        if trade_day and not pd.isna(trade_day):
            trade_day_str = pd.to_datetime(trade_day).strftime('%Y-%m-%d')
            
            if trade_result == 0:
                text.set_text('')
            else:
                text.set_text(f'USD {text.get_text()}\n{trade_day_str}\nTrades: {int(num_trades)}')
        else:
            text.set_text('No trades')
    
    plt.title('Trade Results Heatmap')
    plt.tight_layout()
    plt.show()

def create_chart_calendar_heatmap_trade_result_summary(trades_journal):
    # Convert to DataFrame
    df = pd.DataFrame(trades_journal).T
    df['Trade day'] = pd.to_datetime(df['Trade day'])
    df['Week'] = df['Trade day'].dt.isocalendar().week
    df['Day'] = df['Trade day'].dt.day_name()
    df['Month'] = df['Trade day'].dt.strftime('%B')  # Extract month names

    # Pivot the table for both Total Result and Trade Day
    heatmap_trade_result_data = df.pivot(index='Week', columns='Day', values='Total Result').fillna(0)
    trade_days_data = df.pivot(index='Week', columns='Day', values='Trade day').fillna('')

    # Order the days if they exist
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    available_days = [day for day in days_of_week if day in heatmap_trade_result_data.columns]
    heatmap_trade_result_data = heatmap_trade_result_data[available_days]
    trade_days_data = trade_days_data[available_days]

    # Plot
    fig, ax = plt.subplots(figsize=(2, 2))
    
    # Create a mask for Trade Results equal to 0
    mask = heatmap_trade_result_data == 0

    # Define the custom colormap with a spectral transition from red to green, passing through white
    colors = ["#FF0000", "#FFFFFF", "#00FF00"]
    cmap = sns.blend_palette(colors, as_cmap=True, n_colors=256)

    # Set the background color for the masked cells to white
    ax.set_facecolor('white')

    # Plot the heatmap with the mask applied
    sns.heatmap(heatmap_trade_result_data, cmap=cmap, center=0, annot=False, fmt=".2f", cbar=False, square=True, ax=ax, linewidths=.5, mask=mask)

    # Set Y-axis labels to the month names
    unique_months = df['Month'].unique()
    ax.set_yticks(range(len(unique_months)))
    ax.set_yticklabels(unique_months, rotation=0)
	# Remove the Y-axis label "Week"
    ax.set_ylabel('')

    plt.title('Trade Results Heatmap')
    plt.tight_layout()
    plt.show()



# Assuming you have the 'trades' list of trades available
trades_journal = create_trades_journal(trades)

# Now call the function to create the chart using the trades_journal data
#create_chart_trade_result_by_day(trades_journal)
create_chart_cumulative_trade_result_by_day(trades_journal)
#create_chart_calendar_heatmap_trade_result_by_day(trades_journal)
#create_chart_calendar_heatmap_trade_result_summary(trades_journal)



