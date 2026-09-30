import numpy as np
import pandas as pd

# For reproducible results
np.random.seed(42)

# Number of customers
n_customers = 600

# Generate three types of customer groups
n_per_cluster = n_customers // 3

# Cluster 1: Lower income, lower spending
income_1 = np.random.normal(30, 8, n_per_cluster)
spending_1 = np.random.normal(30, 10, n_per_cluster)

# Cluster 2: Higher income, higher spending
income_2 = np.random.normal(75, 12, n_per_cluster)
spending_2 = np.random.normal(75, 10, n_per_cluster)

# Cluster 3: Higher income, lower spending
income_3 = np.random.normal(70, 12, n_per_cluster)
spending_3 = np.random.normal(30, 10, n_per_cluster)

# Combine the data
annual_income = np.concatenate([
    income_1,
    income_2,
    income_3
])

spending_score = np.concatenate([
    spending_1,
    spending_2,
    spending_3
])

# Keep values within reasonable ranges
annual_income = np.clip(annual_income, 10, 120)
spending_score = np.clip(spending_score, 1, 100)

# Create DataFrame
customers = pd.DataFrame({
    "annual_income_k": annual_income.round(2),
    "spending_score": spending_score.round(2)
})

# Save dataset
customers.to_csv("customers.csv", index=False)

print("Customer dataset generated successfully!")
print(f"Total customers: {len(customers)}")
print("\nFirst 5 records:")
print(customers.head())