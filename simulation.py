import random
import itertools
import statistics
import matplotlib.pyplot as plt

def create_simulation(simulations, 
                      investment,
                      days_to_simulate,
                      max_order_amount,
                      trades_statistics):
	
    order_size_percentage = trades_statistics["Average Amount"] / investment

    trades_per_day = int(round(trades_statistics["Average Trades per day"]))
    trades_to_simulate = trades_per_day * days_to_simulate
	

    def list_trades(investment):
        
        trades = []
        highest_amount = 0
        trades_quantity = 0

        def get_order_amount():
            order_amount = order_size_percentage * investment
            actual_order_amount = min(order_amount, max_order_amount)
            return actual_order_amount

        while trades_quantity < trades_to_simulate:
            trade_result = trades_statistics["Average Gain %"] * get_order_amount() if random.random() < trades_statistics["Win Rate %"] else trades_statistics["Average Loss %"] * get_order_amount()
            investment += trade_result
            highest_amount = max(highest_amount, investment)
            trades.append(trade_result)
            trades_quantity += 1
			
        return trades
		
    #trades = list_trades(investment)
    #print("------------------")
    #print(trades)

    def agg_trades_intraday(trades, trades_day):
        trade_result_intraday = [sum(trades[i:i+trades_day]) for i in range(0, len(trades), trades_day)]
        return trade_result_intraday

    #trade_result_intraday = agg_trades_intraday(trades, trades_day)
    #print("------------------")
    #print(trade_result_intraday)

	#Simulate the trades multiple ties and collect statitics 
    def simulate_trades():
        simulated_trades = []
        for i in range(simulations):
            trade_result_intraday = agg_trades_intraday(list_trades(investment), trades_per_day)
            simulated_trades.append({'Trades Result per Day': trade_result_intraday,
									 'Trade Result Sum': sum(trade_result_intraday)
									})
    
        #Find highest and lowest
        highest_simulated_trades = max(simulated_trades, key=lambda x: x['Trade Result Sum'])
        lowest_simulated_trades = min(simulated_trades, key=lambda x: x['Trade Result Sum'])
        #print("------------------")
        #print(highest_simulated_trades)
        #print(lowest_simulated_trades)
		
		#Collecting only the trades results
        highest_simulated_trades = highest_simulated_trades['Trades Result per Day']
        lowest_simulated_trades = lowest_simulated_trades['Trades Result per Day']
     
		#print("------------------")
        #print(highest_simulated_trades)
        #print(lowest_simulated_trades)

		
		# Calculate Average 
        all_trade_result_sum = [simulated_trade['Trade Result Sum'] for simulated_trade in simulated_trades]
        average_simulated_trades_sum = sum(all_trade_result_sum) / len(all_trade_result_sum)
        #print("------------------")
        #print(average_simulated_trades_sum)

        # Find the item closest to average_simulated_trades
        closest_simulated_trades_to_average_simulated_trades_sum = min(simulated_trades, key=lambda x: abs(x['Trade Result Sum'] - average_simulated_trades_sum))
        average_simulated_trades = closest_simulated_trades_to_average_simulated_trades_sum['Trades Result per Day']

        #print("------------------")
        #print(average_simulated_trades)
        
        # Calculate standard deviation
        std_deviation = statistics.stdev(all_trade_result_sum)

        # Find the lists closest to std deviation * 2 and std deviation * -2
        closest_simulated_trades_to_std_dev_plus_2_simulated_trades = min(simulated_trades, key=lambda x: abs(x['Trade Result Sum'] - (average_simulated_trades_sum + std_deviation * 2)))
        std_dev_plus_2_simulated_trades = closest_simulated_trades_to_std_dev_plus_2_simulated_trades['Trades Result per Day']


        closest_simulated_trades_to_std_dev_minus_2_simulated_trades = min(simulated_trades, key=lambda x: abs(x['Trade Result Sum'] - (average_simulated_trades_sum - std_deviation * 2)))
        std_dev_minus_2_simulated_trades = closest_simulated_trades_to_std_dev_minus_2_simulated_trades['Trades Result per Day']

        #print(std_dev_plus_2_simulated_trades)
        #print(std_dev_minus_2_simulated_trades)

        return simulated_trades, highest_simulated_trades, lowest_simulated_trades, average_simulated_trades, std_dev_plus_2_simulated_trades, std_dev_minus_2_simulated_trades

    simulated_trades, highest_simulated_trades, lowest_simulated_trades, average_simulated_trades, std_dev_plus_2_simulated_trades, std_dev_minus_2_simulated_trades = simulate_trades()

    def accumulate_trades_intraday(choosen_simulated_trades):
        accumulated_trades_intraday = list(itertools.accumulate(choosen_simulated_trades))
        return accumulated_trades_intraday

    #print("------------------")
    #print(accumulate_trades_intraday(highest_simulated_trades))
    #print("------------------")
    #print(accumulate_trades_intraday(lowest_simulated_trades))
    line_highest = accumulate_trades_intraday(highest_simulated_trades)
    line_plus_std_2 = accumulate_trades_intraday(std_dev_plus_2_simulated_trades)
    line_average = accumulate_trades_intraday(average_simulated_trades)
    line_minus_std_2 = accumulate_trades_intraday(std_dev_minus_2_simulated_trades)
    line_lowest = accumulate_trades_intraday(lowest_simulated_trades)
    

	
	# Generate x-axis values (assuming each value represents a day)
    x = list(range(1, len(line_average) + 1))
	
	# Plot the data
    plt.plot(x, line_highest, label='Highest Simulation', color='grey', linestyle=':')
    plt.plot(x, line_plus_std_2, label='2 stddev - Optimistic', color='blue')
    plt.plot(x, line_average, label='Average Simulation', color='green')
    plt.plot(x, line_minus_std_2, label='-2 stddev - Pessimistc', color='blue')
    plt.plot(x, line_lowest, label='Lowest Simulation', color='grey', linestyle=':')

    plt.xlabel('Days')
    plt.ylabel('Trade Result Sum')
    plt.title(f'Trade Result projection for {days_to_simulate} days after {simulations} Simulations')
    plt.legend()
    plt.grid(True)
	
	# Show the plot
    plt.show()





