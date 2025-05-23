import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Number of records to generate
X = 10000  # Change this value as needed

# Sample dimension key lists
num_keys = 5
dim_keys = {
    "customer_id": [f"C{100+i}" for i in range(num_keys)],
    "account_id": [f"A{100+i}" for i in range(num_keys)],
    "product_id": [f"P{100+i}" for i in range(num_keys)],
    "branch_id": [f"B{100+i}" for i in range(num_keys)],
    "transaction_type_id": [f"TT{i+1}" for i in range(num_keys)],
    "currency_id": [f"CUR{i+1}" for i in range(num_keys)],
    "channel_id": [f"CH{i+1}" for i in range(num_keys)],
    "region_id": [f"R{i+1}" for i in range(num_keys)],
    "employee_id": [f"E{i+1}" for i in range(num_keys)],
    "risk_score_id": [f"RS{i+1}" for i in range(num_keys)],
    "merchant_id": [f"M{i+1}" for i in range(num_keys)],
    "loan_type_id": [f"LT{i+1}" for i in range(num_keys)],
    "fraud_status_id": [f"FS{i+1}" for i in range(num_keys)],
    "payment_mode_id": [f"PM{i+1}" for i in range(num_keys)],
    "time_id": [f"T{i+1}" for i in range(num_keys)],
    "tax_code_id": [f"TX{i+1}" for i in range(num_keys)],
    "credit_rating_id": [f"CR{i+1}" for i in range(num_keys)],
    "investment_plan_id": [f"IP{i+1}" for i in range(num_keys)],
    "policy_id": [f"PO{i+1}" for i in range(num_keys)]
}

# Generate random dates
start_date = datetime(2024, 1, 1)
date_range = [start_date + timedelta(days=i) for i in range(365)]
date_keys = [int(d.strftime("%Y%m%d")) for d in date_range]

# Generate the fact table
fact_df = pd.DataFrame({
    "transaction_id": [f"T{i+1}" for i in range(X)],
    "transaction_date_key": np.random.choice(date_keys, X),
    "customer_id": np.random.choice(dim_keys["customer_id"], X),
    "account_id": np.random.choice(dim_keys["account_id"], X),
    "product_id": np.random.choice(dim_keys["product_id"], X),
    "branch_id": np.random.choice(dim_keys["branch_id"], X),
    "transaction_type_id": np.random.choice(dim_keys["transaction_type_id"], X),
    "currency_id": np.random.choice(dim_keys["currency_id"], X),
    "channel_id": np.random.choice(dim_keys["channel_id"], X),
    "region_id": np.random.choice(dim_keys["region_id"], X),
    "employee_id": np.random.choice(dim_keys["employee_id"], X),
    "risk_score_id": np.random.choice(dim_keys["risk_score_id"], X),
    "merchant_id": np.random.choice(dim_keys["merchant_id"], X),
    "loan_type_id": np.random.choice(dim_keys["loan_type_id"], X),
    "fraud_status_id": np.random.choice(dim_keys["fraud_status_id"], X),
    "payment_mode_id": np.random.choice(dim_keys["payment_mode_id"], X),
    "time_id": np.random.choice(dim_keys["time_id"], X),
    "tax_code_id": np.random.choice(dim_keys["tax_code_id"], X),
    "credit_rating_id": np.random.choice(dim_keys["credit_rating_id"], X),
    "investment_plan_id": np.random.choice(dim_keys["investment_plan_id"], X),
    "policy_id": np.random.choice(dim_keys["policy_id"], X),
    "amount": np.round(np.random.uniform(10.0, 10000.0, X), 2)
})

# Save to CSV
fact_df.to_csv("fact_financial_transactions_large.csv", index=False)
print("Generated fact table with", X, "records.")
