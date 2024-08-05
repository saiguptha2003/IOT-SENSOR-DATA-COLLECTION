from datetime import datetime
import pytz

# Set the timezone to Asia/Kolkata
tz = pytz.timezone('Asia/Kolkata')

# Get the current time in the specified timezone
current_time = datetime.now(tz)

# Format the timestamp to a readable string
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

print("Current time in Asia/Kolkata timezone:", formatted_time)
