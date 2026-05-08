"""
Generates a realistic mock grocery transaction dataset for testing the dashboard.

Usage:
    python generatesDataset.py

Output:
    mock_transactions.csv  —  500 transactions across 100 customers (Jan 2024 – Feb 2025)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NUM_TRANSACTIONS = 500
NUM_CUSTOMERS = 100
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 2, 28)

customer_ids = [f"C{str(i).zfill(3)}" for i in range(1, NUM_CUSTOMERS + 1)]
data = []

for _ in range(NUM_TRANSACTIONS):
    # Beta distribution skews purchases so a minority of customers buy far more often,
    # which creates realistic RFM spread across all four segments.
    cust_index = min(int(np.random.beta(0.5, 0.5) * NUM_CUSTOMERS), NUM_CUSTOMERS - 1)
    customer_id = customer_ids[cust_index]

    random_days = random.randint(0, (END_DATE - START_DATE).days)
    invoice_date = (START_DATE + timedelta(days=random_days)).strftime("%d-%m-%Y")
    amount = random.randint(150, 5000)

    data.append([customer_id, invoice_date, "temp", amount])

df = pd.DataFrame(data, columns=["customer_id", "invoice_date", "invoice_no", "amount"])
df["_sort_date"] = pd.to_datetime(df["invoice_date"], format="%d-%m-%Y")
df = df.sort_values("_sort_date").drop("_sort_date", axis=1).reset_index(drop=True)
df["invoice_no"] = [f"INV{str(i + 1).zfill(4)}" for i in range(len(df))]

filename = "mock_transactions.csv"
df.to_csv(filename, index=False)

print(f"✅ Saved {len(df)} rows to '{filename}'.")
print(df.head())
