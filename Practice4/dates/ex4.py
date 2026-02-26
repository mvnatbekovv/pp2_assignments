from datetime import datetime

date1 = datetime(2025, 2, 10, 12, 0, 0)
date2 = datetime(2025, 2, 15, 12, 0, 0)

difference = date2 - date1
seconds = difference.total_seconds()

print("Difference in seconds:", seconds)