from fastapi import FastAPI, HTTPException, Request, Response
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import os
import joblib
import shap
from dotenv import load_dotenv
import uuid
import httpx


import predict as predict_module
import explain as explain_module

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "http://52.220.183.143:8000")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))

print(f"LLM_API_URL = {LLM_API_URL}", flush=True)

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

        # Connect to LLM planning module
        try:
            user_input = {k: v for k, v in data.items() if k != "Sex"}
            llm_payload = {
                "request_id": str(uuid.uuid4()),
                "user_input": user_input,
                "model_output": {
                    "prediction": result["prediction"],
                    "probabilities": result["probabilities"],
                },
                "shap_json": {
                    "base_value": result["explanation"]["base_value"],
                    "values": result["explanation"]["shap_values"],
                },
            }
            llm_resp = httpx.post(
                f"{LLM_API_URL}/api/v1/plan/external",
                json=llm_payload,
                timeout=LLM_TIMEOUT,
            )
            llm_resp.raise_for_status()
            result["advice"] = llm_resp.json()
        except Exception as e:
            result["advice"] = None        # non-fatal — scoring still returns
            result["advice_error"] = str(e)

        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")