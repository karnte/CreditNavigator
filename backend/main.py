from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from google.cloud import aiplatform

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------
# FastAPI setup
# ------------------------------------------------------
app = FastAPI(title="Credit Risk Predictor API")

# Get allowed origins from environment variable
allowed_origins_str = os.getenv(
    "https://credit-frontend-558345680759.us-west2.run.app",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080"
)
# Split by comma and strip whitespace
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

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
    Gender: Literal["Male", "Female"]
    Married: Literal["Y", "N"]
    Dependents: int = Field(ge=0)
    Education: Literal["Graduate", "Undergraduate"]
    Self_Employed: Literal["Y", "N"]
    ApplicantIncome: float = Field(ge=0)
    CoapplicantIncome: float = Field(ge=0)
    LoanAmount: float = Field(ge=0)
    Loan_Amount_Term: float = Field(ge=0)
    Credit_History: Literal["1", "0"]
    Property_Area: Literal["Urban", "Semi Urban", "Rural"]

# ------------------------------------------------------
# Vertex AI config
# ------------------------------------------------------
PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "cloud-ml-project-477817")
LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID", "7091875287922638848")

# ------------------------------------------------------
# Vertex AI helpers
# ------------------------------------------------------
def call_vertex_ai(instances: list[dict]) -> list:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"
    )
    prediction = endpoint.predict(instances=instances)
    return prediction.predictions


def preprocess_to_vertex_payload(data: CreditInput) -> dict:
    """Prepare payload for Vertex AI — auto Loan_ID and proper types."""
    loan_id = f"AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    payload = {
        "Loan_ID": loan_id,
        "Gender": str(data.Gender),
        "Married": str(data.Married),
        "Dependents": str(data.Dependents),
        "Education": str(data.Education),
        "Self_Employed": str(data.Self_Employed),
        "ApplicantIncome": str(data.ApplicantIncome),
        "CoapplicantIncome": str(data.CoapplicantIncome),
        "LoanAmount": str(data.LoanAmount),
        "Loan_Amount_Term": str(data.Loan_Amount_Term),
        "Credit_History": str(data.Credit_History),
        "Property_Area": str(data.Property_Area),
    }
    return payload

# ------------------------------------------------------
# Predict endpoint
# ------------------------------------------------------
@app.options("/predict")
def preflight_handler():
    return {"message": "ok"}
@app.post("/predict")
def predict(payload: CreditInput):
    vertex_payload = preprocess_to_vertex_payload(payload)

    try:
        preds = call_vertex_ai([vertex_payload])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vertex AI call failed: {str(e)}")

    if not preds:
        raise HTTPException(status_code=500, detail="Empty prediction response from Vertex AI.")

    raw_pred = preds[0]
    print("🧠 Vertex raw response:", preds)

    if not isinstance(raw_pred, dict):
        raise HTTPException(status_code=500, detail=f"Unexpected prediction format: {type(raw_pred)}")

    scores = raw_pred.get("scores")
    classes = raw_pred.get("classes")

    if not scores or not classes or len(scores) != len(classes):
        raise HTTPException(status_code=500, detail=f"Invalid Vertex AI response structure: {raw_pred}")

    # Pick class with highest probability
    max_idx = scores.index(max(scores))
    pred_class = classes[max_idx]

    # Map Y/N to binary for frontend (1=Low Risk, 0=High Risk)
    if pred_class.upper() == "Y":
        pred_value = 1
    elif pred_class.upper() == "N":
        pred_value = 0
    else:
        raise HTTPException(status_code=500, detail=f"Unexpected class label: {pred_class}")

    return {"prediction": pred_value}
