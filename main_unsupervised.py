from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import joblib
import os


# --------------------------------------------------
# Initialize FastAPI
# --------------------------------------------------

app = FastAPI(
    title="Customer Persona Segmenter API",
    description="API for customer persona prediction using K-Means clustering",
    version="1.0.0"
)


# --------------------------------------------------
# Model Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
KMEANS_PATH = os.path.join(MODEL_DIR, "kmeans_model.pkl")
PERSONA_PATH = os.path.join(MODEL_DIR, "cluster_personas.pkl")


# --------------------------------------------------
# Load Trained Models
# --------------------------------------------------

try:
    scaler = joblib.load(SCALER_PATH)
    kmeans = joblib.load(KMEANS_PATH)
    cluster_personas = joblib.load(PERSONA_PATH)

except Exception as e:
    scaler = None
    kmeans = None
    cluster_personas = None
    print(f"Model loading error: {e}")


# --------------------------------------------------
# Request Schema
# --------------------------------------------------

class CustomerInput(BaseModel):
    annual_income_k: float = Field(..., gt=0)
    spending_score: float = Field(..., ge=0, le=100)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Customer Persona Segmenter API is running",
        "status": "success"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():

    if scaler is None or kmeans is None or cluster_personas is None:
        return {
            "status": "unhealthy",
            "model_loaded": False
        }

    return {
        "status": "healthy",
        "model_loaded": True
    }

# --------------------------------------------------
# Persona Information Endpoint
# --------------------------------------------------

@app.get("/personas")
def get_personas():

    if cluster_personas is None:
        raise HTTPException(
            status_code=500,
            detail="Persona information is not loaded"
        )

    personas = []

    for cluster, details in cluster_personas.items():
        personas.append({
            "cluster": int(cluster),
            "persona": details["persona"],
            "annual_income_k": details["annual_income_k"],
            "spending_score": details["spending_score"]
        })

    personas.sort(key=lambda x: x["cluster"])

    return {
        "count": len(personas),
        "personas": personas
    }


# --------------------------------------------------
# Prediction Endpoint
# --------------------------------------------------

@app.post("/predict")
def predict_persona(customer: CustomerInput):

    if scaler is None or kmeans is None or cluster_personas is None:
        raise HTTPException(
            status_code=500,
            detail="ML model is not loaded"
        )

    # Convert input into DataFrame
    input_data = pd.DataFrame([
        {
            "annual_income_k": customer.annual_income_k,
            "spending_score": customer.spending_score
        }
    ])

    # Apply the same scaler used during training
    input_scaled = scaler.transform(input_data)

    # Predict cluster
    cluster = int(kmeans.predict(input_scaled)[0])

    # Get persona information
    persona_info = cluster_personas.get(cluster)

    if persona_info is None:
        raise HTTPException(
            status_code=500,
            detail="Persona information not found"
        )

    return {
        "annual_income_k": customer.annual_income_k,
        "spending_score": customer.spending_score,
        "cluster": cluster,
        "persona": persona_info["persona"]
    }