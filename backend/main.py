from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import os
import pickle

import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------
# FastAPI setup
# ------------------------------------------------------
app = FastAPI(title="Credit Risk Predictor API")

# CORS Configuration - Simplified and explicit
allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://credit-frontend-558345680759.us-west2.run.app",
]

# Also check environment variable
env_origins = os.getenv("FRONTEND_URL", "")
if env_origins:
    for origin in env_origins.split(","):
        origin = origin.strip()
        if origin and origin not in allowed_origins:
            allowed_origins.append(origin)

print(f"Allowed CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# Input schema
# ------------------------------------------------------
class CreditInput(BaseModel):
    Sex: Literal["Male", "Female"]
    Occupation: str
    Salary: float = Field(ge=0)
    Marriage_Status: Literal["Single", "Married", "Divorced", "Widowed"]
    credit_score: float = Field(ge=0)
    credit_grade: str
    outstanding: float = Field(ge=0)
    Coapplicant: Literal["Yes", "No"]
    loan_amount: float = Field(ge=0)
    loan_term: float = Field(gt=0)
    Interest_rate: float = Field(ge=0)


# ------------------------------------------------------
# Local model config
# ------------------------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.pkl"))
MODEL = None


def load_model() -> None:
    global MODEL
    if MODEL is None:
        try:
            with open(MODEL_PATH, "rb") as model_file:
                MODEL = pickle.load(model_file)
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Model file not found at '{MODEL_PATH}'. Place model.pkl in backend/ or set MODEL_PATH."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to load model from '{MODEL_PATH}': {exc}") from exc


@app.on_event("startup")
def startup_event() -> None:
    load_model()


# ------------------------------------------------------
# Prediction helpers
# ------------------------------------------------------
def preprocess_to_model_input(data: CreditInput) -> pd.DataFrame:
    """Prepare payload for the local model with the expected feature order."""
    payload = {
        "Sex": data.Sex,
        "Occupation": data.Occupation,
        "Salary": data.Salary,
        "Marriage_Status": data.Marriage_Status,
        "credit_score": data.credit_score,
        "credit_grade": data.credit_grade,
        "outstanding": data.outstanding,
        "Coapplicant": data.Coapplicant,
        "loan_amount": data.loan_amount,
        "loan_term": data.loan_term,
        "Interest_rate": data.Interest_rate,
    }
    return pd.DataFrame([payload])


# ------------------------------------------------------
# Predict endpoint
# ------------------------------------------------------

# Explicit OPTIONS handler for CORS preflight
@app.options("/predict")
async def options_predict(request: Request):
    """Handle CORS preflight requests"""

    # Return 200 OK with CORS headers
    # The CORS middleware will add the appropriate headers
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        },
    )


@app.post("/predict")
def predict(payload: CreditInput):
    try:
        load_model()
        model_input = preprocess_to_model_input(payload)

        raw_pred = MODEL.predict(model_input)[0]

        if hasattr(MODEL, "predict_proba"):
            probabilities = MODEL.predict_proba(model_input)[0].tolist()
        else:
            probabilities = None

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

    return {
        "prediction": int(raw_pred) if str(raw_pred).isdigit() else str(raw_pred),
        "probabilities": probabilities,
    }
