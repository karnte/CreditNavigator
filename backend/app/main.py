from fastapi import FastAPI, HTTPException, Request, Response
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import os
import joblib
import shap
from dotenv import load_dotenv

import predict as predict_module
import explain as explain_module

load_dotenv()


MODEL = None
EXPLAINER = None
MODEL_PATH = os.getenv("MODEL_PATH")

if not MODEL_PATH:
    raise RuntimeError("MODEL_PATH environment variable is not set")

def load_model():
    global MODEL, EXPLAINER

    if MODEL is not None:
        return

    model_path = (Path(__file__).parent.parent / MODEL_PATH).resolve()
    print("Loading model from:", model_path)

    if not model_path.exists():
        raise RuntimeError(f"Model not found: {model_path}")

    MODEL = joblib.load(model_path)
    lgbm_model = MODEL.named_steps['lgbm']
    EXPLAINER = shap.TreeExplainer(lgbm_model)

    print("Model loaded successfully")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title="Credit Risk Predictor API", lifespan=lifespan)


# Schema 
class CreditInput(BaseModel):
    Sex: Literal["Male", "Female"]
    Occupation: str
    Salary: float = Field(ge=0)
    Marriage_Status: Literal["Single", "Married", "Divorced", "Widowed"]
    credit_score: float = Field(ge=0)
    credit_grade: str
    outstanding: float = Field(ge=0)
    overdue: float = Field(ge=0)
    Coapplicant: int = Field(ge=0, le=1)
    loan_amount: float = Field(ge=0)
    loan_term: float = Field(gt=0)
    Interest_rate: float = Field(ge=0)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Credit Risk Predictor API. Use /docs."}


@app.post("/predict")
def predict(payload: CreditInput):
    try:
        data = payload.model_dump()

        result = predict_module.run_prediction(data, MODEL)
        result["explanation"] = explain_module.compute_shap(data, MODEL, EXPLAINER)

        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
