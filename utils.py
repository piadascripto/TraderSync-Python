def simplify_time_difference(initial_date, end_date):
	time_difference = end_date - initial_date
	if time_difference.total_seconds() < 60:  # Less than 60 minutes
		seconds_apart = time_difference.total_seconds()
		simple_time_difference = str(int(seconds_apart)) + " second" + ("s" if seconds_apart != 1 else "")
	elif time_difference.total_seconds() < 3600:  # Less than 60 minutes
		minutes_apart = time_difference.total_seconds() // 60
		simple_time_difference = str(int(minutes_apart)) + " minute" + ("s" if minutes_apart != 1 else "")
	elif initial_date.date() == end_date.date():  # Same day
		hours_apart = time_difference.total_seconds() // 3600
		simple_time_difference = str(int(hours_apart)) + " hour" + ("s" if hours_apart != 1 else "") 
	else:  # Different days
		days_apart = (end_date.date() - initial_date.date()).days
		simple_time_difference = str(days_apart) + " day" + ("s" if days_apart != 1 else "")

	return simple_time_difference
