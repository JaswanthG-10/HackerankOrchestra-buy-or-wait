import pandas as pd
from datetime import datetime, timedelta

# User 10 simulation from 2024-12-06
start_dt = datetime.strptime("2024-12-06", "%Y-%m-%d")
bal = 750155.0
min_bal = 225400.0

traj = []
# Weekly groceries on Thursdays (weekday 3)
# Weekly transport on Fridays (weekday 4)
# Bi-weekly dining on Saturdays (weekday 5)
# Rent on day 3 of month
# Utilities on day 7 of month
# Gym on day 11 of month
# Music on day 12 of month
# Delivery on day 14 of month
# Cinema on day 15 of month

min_seen = bal
min_date = None

for d in range(90):
    dt = start_dt + timedelta(days=d)
    outflow = 0.0
    
    # Check monthly
    if dt.day == 3 and d > 0: outflow += 69100.0 # Rent (Dec 3 already passed)
    if dt.day == 7: outflow += 17103.95 # Utilities
    if dt.day == 11: outflow += 4860.0 # Gym
    if dt.day == 12: outflow += 2800.0 # Music
    if dt.day == 14: outflow += 1895.0 # Delivery
    if dt.day == 15: outflow += 4645.19 # Cinema
    
    # Weekly groceries (Thursday = weekday 3)
    if dt.weekday() == 3: outflow += 10776.07
    # Weekly transport (Friday = weekday 4)
    if dt.weekday() == 4: outflow += 5982.79
    
    bal -= outflow
    if bal < min_seen:
        min_seen = bal
        min_date = dt.strftime("%Y-%m-%d")
    traj.append((dt.strftime("%Y-%m-%d"), bal, outflow))

print(f"Ending Balance on day 90: {bal:.2f}")
print(f"Minimum Balance: {min_seen:.2f} on {min_date}")
print(f"Headroom above min_bal ({min_bal}): {min_seen - min_bal:.2f}")
print(f"Target Safe Amount for request_10: 12700.0")
