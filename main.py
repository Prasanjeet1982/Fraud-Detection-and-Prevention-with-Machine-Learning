# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

app = FastAPI()

class TransactionData(BaseModel):
    """
    Pydantic model to represent transaction data sent to the /predict/ endpoint.
    """
    amount: float
    merchant: str
    location: str

@app.on_event("startup")
async def load_model():
    """
    Load the trained model and scaler on application startup.
    """
    global model, scaler
    model = joblib.load("fraud_model.pkl")
    scaler = joblib.load("scaler.pkl")

@app.post("/predict/")
async def predict_fraud(transaction: TransactionData):
    """
    Endpoint to predict whether a transaction is fraudulent or not.

    Args:
        transaction (TransactionData): Transaction data including amount, merchant, and location.

    Returns:
        dict: Prediction result indicating whether the transaction is fraudulent.
    """
    try:
        features = pd.DataFrame({
            "amount": [transaction.amount],
            "merchant": [transaction.merchant],
            "location": [transaction.location]
        })

        # Preprocess data and scale features
        scaled_features = scaler.transform(features)

        # Predict fraud
        prediction = model.predict(scaled_features)
        
        if prediction[0] == 1:
            return {"fraudulent": True}
        else:
            return {"fraudulent": False}
    except Exception:
        raise HTTPException(status_code=500, detail="Prediction failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
