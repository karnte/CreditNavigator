from fastapi import FastAPI, HTTPException, Request, Response
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import os
import pandas as pd
import joblib
from dotenv import load_dotenv

load_dotenv()


MODEL = None
MODEL_PATH = os.getenv("MODEL_PATH")
model_path = (Path(__file__).parent / MODEL_PATH).resolve()
if not MODEL_PATH:
    raise RuntimeError("MODEL_PATH environment variable is not set")

def load_model():
    global MODEL

    if MODEL is not None:
        return

    model_path = Path(MODEL_PATH).resolve()
    print("Loading model from:", model_path)

    if not model_path.exists():
        raise RuntimeError(f"Model not found: {model_path}")

    MODEL = joblib.load(model_path)

    print("Model loaded successfully")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title="Credit Risk Predictor API", lifespan=lifespan)

# # --- CORS ---
# allowed_origins = [
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://credit-frontend-558345680759.us-west2.run.app",
# ]
# env_origins = os.getenv("FRONTEND_URL", "")
# if env_origins:
#     for origin in env_origins.split(","):
#         origin = origin.strip()
#         if origin and origin not in allowed_origins:
#             allowed_origins.append(origin)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# --- Schema ---
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

def preprocess_to_model_input(data: CreditInput) -> pd.DataFrame:
    salary = float(data.Salary)
    denom = salary if salary > 0 else 1e-9

    payload = {
        "Sex": data.Sex,
        "Occupation": data.Occupation,
        "Salary": salary,
        "Marriage_Status": data.Marriage_Status,
        "credit_score": float(data.credit_score),
        "credit_grade": data.credit_grade,
        "outstanding": float(data.outstanding),
        "overdue": float(data.overdue),
        "Coapplicant": data.Coapplicant,
        "loan_amount": float(data.loan_amount),
        "loan_term": float(data.loan_term),
        "Interest_rate": float(data.Interest_rate),

        # engineered
        "has_overdue": 1 if data.overdue > 0 else 0,
        "dti": float(data.outstanding) / denom,
        "lti": float(data.loan_amount) / denom,
    }

    df = pd.DataFrame([payload])

    # enforce the exact columns + order the pipeline was trained with
    if hasattr(MODEL, "feature_names_in_"):
        required = list(MODEL.feature_names_in_)
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required features: {missing}")
        df = df[required]

    return df

@app.get("/")
def read_root():
    return {"message": "Welcome to the Credit Risk Predictor API. Use /docs."}

# @app.options("/predict")
# async def options_predict(request: Request):
#     return Response(
#         status_code=200,
#         headers={
#             "Access-Control-Allow-Methods": "POST, OPTIONS",
#             "Access-Control-Allow-Headers": "Content-Type",
#             "Access-Control-Max-Age": "3600",
#         },
#     )

@app.post("/predict")
def predict(payload: CreditInput):
    try:
        model_input = preprocess_to_model_input(payload)
        classes = MODEL.classes_

        raw_pred = MODEL.predict(model_input)[0]
        proba = MODEL.predict_proba(model_input)[0].tolist() if hasattr(MODEL, "predict_proba") else None
        prob_dict = {str(classes[i]): float(proba[i]) for i in range(len(classes))}

        return {
            "prediction": int(raw_pred),
            "probabilities": prob_dict
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")