import os
import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

data = pd.read_csv("customers.csv")

print("Dataset loaded successfully!")
print(f"Number of customers: {len(data)}")


# --------------------------------------------------
# 2. Select Features
# --------------------------------------------------

features = [
    "annual_income_k",
    "spending_score"
]

X = data[features]


# --------------------------------------------------
# 3. Scale Features
# --------------------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# --------------------------------------------------
# 4. Train K-Means Model
# --------------------------------------------------

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

clusters = kmeans.fit_predict(X_scaled)


# Add cluster number to dataset
data["cluster"] = clusters


# --------------------------------------------------
# 5. Analyze Cluster Centroids
# --------------------------------------------------

centroids_scaled = kmeans.cluster_centers_

# Convert centroids back to original scale
centroids = scaler.inverse_transform(centroids_scaled)

centroid_df = pd.DataFrame(
    centroids,
    columns=features
)

centroid_df["cluster"] = range(3)


print("\nCluster Centroids:")
print(centroid_df)


# --------------------------------------------------
# 6. Map Clusters to Customer Personas
# --------------------------------------------------

cluster_personas = {}

for _, row in centroid_df.iterrows():

    cluster = int(row["cluster"])
    income = row["annual_income_k"]
    spending = row["spending_score"]

    if income < 50 and spending < 50:
        persona = "Budget-Conscious Customer"

    elif income >= 50 and spending >= 50:
        persona = "Premium Customer"

    elif income >= 50 and spending < 50:
        persona = "High-Income Low-Spender"

    else:
        persona = "Emerging Spender"

    cluster_personas[cluster] = {
        "persona": persona,
        "annual_income_k": round(float(income), 2),
        "spending_score": round(float(spending), 2)
    }


print("\nCustomer Personas:")

for cluster, details in cluster_personas.items():
    print(f"Cluster {cluster}: {details['persona']}")


# --------------------------------------------------
# 7. Create Models Folder
# --------------------------------------------------

os.makedirs("models", exist_ok=True)


# --------------------------------------------------
# 8. Save Model Artifacts
# --------------------------------------------------

joblib.dump(scaler, "models/scaler.pkl")

joblib.dump(kmeans, "models/kmeans_model.pkl")

joblib.dump(
    cluster_personas,
    "models/cluster_personas.pkl"
)


# --------------------------------------------------
# 9. Save Clustered Dataset
# --------------------------------------------------

data.to_csv("customers.csv", index=False)


print("\nModel training completed successfully!")

print("\nSaved files:")
print("models/scaler.pkl")
print("models/kmeans_model.pkl")
print("models/cluster_personas.pkl")